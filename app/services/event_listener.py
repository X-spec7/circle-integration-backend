import asyncio
import logging
from typing import List

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.project import Project
from app.models.investment import Investment, InvestmentStatus
from app.models.wallet_address import WalletAddress
from app.models.user import User
from compiled_contracts.contract_constants import IEO_ABI
from web3 import Web3
from web3.providers.websocket import WebsocketProvider

logger = logging.getLogger(__name__)

class LiveEventListener:
    def __init__(self):
        self._tasks: List[asyncio.Task] = []
        self._use_ws = False
        self.w3 = None
        # Require WS provider for subscriptions
        if settings.ws_rpc_url:
            try:
                self.w3 = Web3(WebsocketProvider(settings.ws_rpc_url))
                if not self.w3.is_connected():
                    raise Exception("WS not connected")
                logger.info("Using WebSocket provider for live event listening")
                self._use_ws = True
            except Exception as e:
                logger.error(f"WS provider init failed: {e}")
        else:
            logger.error("WS RPC URL not configured; live event listener disabled")

    async def start(self):
        if not self._use_ws or not self.w3:
            logger.error("Live event listener not started (no WS provider)")
            return
        await self._start_project_listeners()

    async def _start_project_listeners(self):
        db = SessionLocal()
        try:
            projects: List[Project] = db.query(Project).filter(Project.ieo_contract_address.isnot(None)).all()
            for project in projects:
                task = asyncio.create_task(self._listen_project_investments(project.id, project.ieo_contract_address))
                self._tasks.append(task)
        finally:
            db.close()

    async def _listen_project_investments(self, project_id: str, ieo_address: str):
        contract = self.w3.eth.contract(address=ieo_address, abi=IEO_ABI)
        event = contract.events.InvestmentMade

        # True subscription style via node-side filter; get_new_entries picks up new logs
        try:
            evt_filter = event.create_filter(fromBlock='latest')
        except Exception as e:
            logger.error(f"Failed to create event filter for project {project_id}: {e}")
            return
        poll_interval = 1
        while True:
            try:
                entries = evt_filter.get_new_entries()
                if entries:
                    await self._handle_logs(project_id, entries)
            except Exception as e:
                logger.error(f"Live WS listener error for project {project_id}: {e}")
                # Attempt to recreate the filter after a brief pause
                await asyncio.sleep(2)
                try:
                    evt_filter = event.create_filter(fromBlock='latest')
                except Exception as e2:
                    logger.error(f"Recreating filter failed for project {project_id}: {e2}")
            await asyncio.sleep(poll_interval)

    async def _handle_logs(self, project_id: str, logs):
        db = SessionLocal()
        try:
            for ev in logs:
                args = ev['args']
                investor_address = str(args.get('investor')).lower()
                usdc_amount_raw = int(args.get('usdcAmount'))
                token_amount_raw = int(args.get('tokenAmount'))
                tx_hash = ev['transactionHash'].hex()
                block_number = ev['blockNumber']

                wallet = db.query(WalletAddress).filter(WalletAddress.address.ilike(investor_address)).first()
                user_id = wallet.user_id if wallet else None
                if not user_id:
                    user = db.query(User).filter(User.wallet_address.ilike(investor_address)).first()
                    user_id = user.id if user else None
                if not user_id:
                    logger.warning(f"Live listener skip unknown wallet {investor_address} (project {project_id}, tx {tx_hash})")
                    continue

                exists = db.query(Investment).filter(
                    Investment.transaction_hash == tx_hash,
                    Investment.project_id == project_id,
                    Investment.investor_id == user_id
                ).first()
                if exists:
                    continue

                from decimal import Decimal
                usdc_amount = Decimal(usdc_amount_raw) / Decimal(1_000_000)
                token_amount = Decimal(token_amount_raw) / Decimal(1_000_000_000_000_000_000)

                inv = Investment(
                    investor_id=user_id,
                    project_id=project_id,
                    usdc_amount=usdc_amount,
                    token_amount=token_amount,
                    investment_time=None,
                    status=InvestmentStatus.CONFIRMED,
                    transaction_hash=tx_hash,
                    block_number=block_number,
                    investor_wallet_address=investor_address,
                )
                db.add(inv)
                db.commit()
        except Exception as e:
            logger.error(f"Error handling live logs for project {project_id}: {e}")
        finally:
            db.close()

live_event_listener = LiveEventListener() 