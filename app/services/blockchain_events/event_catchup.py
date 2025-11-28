import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from web3 import Web3

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.investment import Investment, InvestmentStatus
from app.models.wallet_address import WalletAddress
from app.models.user import User
from app.services.blockchain_service import blockchain_service
from compiled_contracts.contract_constants import IEO_ABI

logger = logging.getLogger(__name__)

BLOCK_POLL_INTERVAL_SECONDS = 60
MAX_BLOCK_RANGE = 2000
MIN_BLOCK_RANGE = 250
MAX_RETRIES = 5
BACKOFF_SECONDS = 2

class BlockchainEventCatchUp:
    def __init__(self):
        self.w3 = blockchain_service.w3

    async def start(self):
        await self.catch_up_all_projects()
        asyncio.create_task(self._poll_loop())

    async def _poll_loop(self):
        while True:
            try:
                await self.catch_up_all_projects()
            except Exception as e:
                logger.error(f"Event catch-up poll error: {e}")
            await asyncio.sleep(BLOCK_POLL_INTERVAL_SECONDS)

    async def catch_up_all_projects(self):
        db = SessionLocal()
        try:
            projects: List[Project] = db.query(Project).filter(Project.ieo_contract_address.isnot(None)).all()
            for project in projects:
                await self._catch_up_project(db, project)
        finally:
            db.close()

    async def _catch_up_project(self, db, project: Project):
        try:
            contract_address = project.ieo_contract_address
            if not contract_address:
                return
            from_block = (project.last_processed_block or 0) + 1
            latest_block = self.w3.eth.block_number
            if from_block > latest_block:
                return

            current_from = from_block
            while current_from <= latest_block:
                target_to = min(current_from + MAX_BLOCK_RANGE - 1, latest_block)
                processed_to = await self._process_investment_events_range(db, project, current_from, target_to)
                if processed_to < current_from:
                    break
                project.last_processed_block = processed_to
                db.commit()
                current_from = processed_to + 1
        except Exception as e:
            logger.error(f"Failed catch-up for project {project.id}: {e}")

    async def _process_investment_events_range(self, db, project: Project, from_block: int, to_block: int) -> int:
        attempt_from = from_block
        attempt_to = to_block
        retries = 0
        while True:
            try:
                contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(project.ieo_contract_address),
                    abi=IEO_ABI
                )
                event_abi = contract.events.InvestmentMade
                logs = event_abi().get_logs(fromBlock=attempt_from, toBlock=attempt_to)
                if logs:
                    for ev in logs:
                        args = ev['args']
                        investor_address = str(args.get('investor')).lower()
                        usdc_amount_raw = int(args.get('usdcAmount'))
                        token_amount_raw = int(args.get('tokenAmount'))
                        tx_hash = ev['transactionHash'].hex()
                        block_number = ev['blockNumber']
                        block = self.w3.eth.get_block(block_number)
                        ts = int(block.timestamp)
                        investment_time = datetime.utcfromtimestamp(ts)

                        wallet = db.query(WalletAddress).filter(WalletAddress.address.ilike(investor_address)).first()
                        user_id: Optional[str] = None
                        if wallet:
                            user_id = wallet.user_id
                        else:
                            user = db.query(User).filter(User.wallet_address.ilike(investor_address)).first()
                            if user:
                                user_id = user.id

                        if not user_id:
                            logger.warning(f"Skipping investment sync for unknown wallet {investor_address} (project {project.id}, tx {tx_hash})")
                            continue

                        exists = db.query(Investment).filter(
                            Investment.transaction_hash == tx_hash,
                            Investment.project_id == project.id,
                            Investment.investor_id == user_id
                        ).first()
                        if exists:
                            continue

                        usdc_amount = Decimal(usdc_amount_raw) / Decimal(1_000_000)
                        token_amount = Decimal(token_amount_raw) / Decimal(1_000_000_000_000_000_000)

                        inv = Investment(
                            investor_id=user_id,
                            project_id=project.id,
                            usdc_amount=usdc_amount,
                            token_amount=token_amount,
                            investment_time=investment_time,
                            status=InvestmentStatus.CONFIRMED,
                            transaction_hash=tx_hash,
                            block_number=block_number,
                            investor_wallet_address=investor_address,
                        )
                        db.add(inv)
                        project.current_raised = (project.current_raised or Decimal(0)) + usdc_amount
                        db.commit()
                return attempt_to
            except Exception as e:
                msg = str(e).lower()
                is_rate_limited = ('too many requests' in msg) or ('status code: 429' in msg) or ('429' in msg)
                if is_rate_limited and retries < MAX_RETRIES:
                    logger.warning(f"Rate limited fetching logs {attempt_from}-{attempt_to}. Retrying with backoff and smaller range...")
                    await asyncio.sleep(BACKOFF_SECONDS * (2 ** retries))
                    current_range = attempt_to - attempt_from + 1
                    new_range = max(MIN_BLOCK_RANGE, current_range // 2)
                    attempt_to = attempt_from + new_range - 1
                    retries += 1
                    continue
                logger.error(f"Error processing events for project {project.id} blocks {attempt_from}-{attempt_to}: {e}")
                return max(attempt_from - 1, from_block - 1)

# Global instance
blockchain_event_catchup = BlockchainEventCatchUp() 