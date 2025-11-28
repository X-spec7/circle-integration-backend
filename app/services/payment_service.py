from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime
from web3 import Web3

from app.models.investment import Investment, PaymentMethod, PaymentStatus
from app.models.payment import Payment
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.models.wallet_address import WalletAddress
from app.services.circle_client import CircleClient
from app.services.blockchain_service import blockchain_service
from compiled_contracts.contract_constants import FUNDRAISINGTOKEN_ABI, IEO_ABI
from app.schemas.payment import InvestmentCreate, PaymentInitiateRequest
from app.core.config import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """Service class for payment and investment operations"""
    
    def __init__(self):
        self.circle_client = CircleClient()
    
    async def create_investment(self, db: Session, user: User, investment_data: InvestmentCreate) -> Investment:
        """Create a new investment record"""
        try:
            # Get the project
            project = db.query(Project).filter(Project.id == investment_data.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Check if project is active
            if project.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project is not active for investments"
                )
            
            # Calculate tokens to receive
            tokens_received = int(investment_data.amount / project.price_per_token)
            
            # Create investment record
            investment = Investment(
                id=str(uuid.uuid4()),
                user_id=user.id,
                project_id=investment_data.project_id,
                amount=investment_data.amount,
                tokens_received=tokens_received,
                payment_method=investment_data.payment_method,
                payment_status=PaymentStatus.PENDING
            )
            
            db.add(investment)
            db.commit()
            db.refresh(investment)
            
            return investment
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating investment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create investment"
            )
    
    async def initiate_payment(
        self,
        db: Session,
        user: User,
        payment_data: PaymentInitiateRequest
    ) -> Dict[str, Any]:
        """Initiate payment for investment"""
        try:
            # Validate project exists and is active
            project = db.query(Project).filter(Project.id == payment_data.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if project.status != ProjectStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project is not active for investments"
                )
            
            # Validate investor wallet provided and whitelisted on token contract
            if not payment_data.investor_wallet_address or not payment_data.investor_wallet_address.startswith('0x') or len(payment_data.investor_wallet_address) != 42:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid investor wallet address format")

            try:
                token_address = project.token_contract_address
                if not token_address:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project token address is not set")
                token_contract = blockchain_service.w3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=FUNDRAISINGTOKEN_ABI
                )
                investor_checksum = Web3.to_checksum_address(payment_data.investor_wallet_address)
                is_whitelisted = token_contract.functions.isWhitelisted(investor_checksum).call()
            except Exception as e:
                logger.error(f"Whitelist check failed: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify wallet whitelist status")

            if not is_whitelisted:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wallet is not whitelisted for this token")

            # Record or upsert wallet ownership mapping
            try:
                existing = db.query(WalletAddress).filter(WalletAddress.address == payment_data.investor_wallet_address).first()
                if not existing:
                    db.add(WalletAddress(user_id=user.id, address=payment_data.investor_wallet_address))
                    db.commit()
                elif existing.user_id != user.id:
                    logger.warning(f"Wallet address {payment_data.investor_wallet_address} already mapped to different user {existing.user_id}")
            except Exception as e:
                logger.error(f"Failed to upsert wallet address mapping: {e}")
            
            # Initiate payment based on method
            if payment_data.payment_method == "fiat":
                result = await self._initiate_fiat_payment(db, None, project)
            elif payment_data.payment_method == "card":
                result = await self._initiate_card_payment(db, None, project)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payment method. Supported: 'fiat' (SEPA) or 'card' (credit/debit)"
                )

            # Persist investor wallet on payment
            try:
                payment = db.query(Payment).filter(Payment.id == result.get("payment_id")).first()
                if payment:
                    payment.investor_wallet_address = payment_data.investor_wallet_address
                    db.commit()
            except Exception as e:
                logger.warning(f"Failed to store investor wallet on payment: {e}")

            return result
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initiate payment"
            )
    # TODO: remove investment props completely
    async def _initiate_fiat_payment(self, db: Session, investment: Optional[Investment], project: Project) -> Dict[str, Any]:
        """Initiate fiat payment through Circle (SEPA Bank Transfer)"""
        try:
            # Create payment record
            payment = Payment(
                id=str(uuid.uuid4()),
                investment_id=None if investment is None else investment.id,
                amount=investment.amount if investment else Decimal('0'),
                currency="EUR",
                payment_method="fiat",
                status=PaymentStatus.PENDING
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            # Create Circle payment intent for SEPA
            description = f"Investment in {project.name} - {payment.amount} EUR"
            circle_response = await self.circle_client.create_payment_intent(
                amount=str(int(payment.amount * 100)),  # Convert to cents
                currency="EUR",
                description=description,
                payment_method="sepaBankAccount"
            )
            
            # Update payment with Circle payment ID
            payment.circle_payment_id = circle_response["data"]["id"]
            db.commit()
            
            # Extract bank details from Circle response
            bank_details = None
            if "data" in circle_response and "paymentMethods" in circle_response["data"]:
                for method in circle_response["data"]["paymentMethods"]:
                    if method.get("type") == "sepaBankAccount":
                        bank_details = {
                            "iban": method.get("iban"),
                            "bic": method.get("bic"),
                            "account_name": method.get("accountName"),
                            "reference": method.get("reference")
                        }
                        break
            
            return {
                "payment_id": payment.id,
                "status": "pending",
                "payment_method": "sepa_bank_transfer",
                "bank_details": bank_details,
                "message": "Please transfer the amount to the provided bank account. Your investment will be processed once payment is confirmed."
            }
            
        except Exception as e:
            logger.error(f"Error initiating fiat payment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initiate fiat payment"
            )
    
    async def _initiate_card_payment(self, db: Session, investment: Optional[Investment], project: Project) -> Dict[str, Any]:
        """Initiate card payment through Circle"""
        try:
            # Create payment record
            payment = Payment(
                id=str(uuid.uuid4()),
                investment_id=None if investment is None else investment.id,
                amount=investment.amount if investment else Decimal('0'),
                currency="EUR",
                payment_method="card",
                status=PaymentStatus.PENDING
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            # Create Circle payment intent for card
            description = f"Investment in {project.name} - {payment.amount} EUR"
            circle_response = await self.circle_client.create_payment_intent(
                amount=str(int(payment.amount * 100)),  # Convert to cents
                currency="EUR",
                description=description,
                payment_method="card"
            )
            
            # Update payment with Circle payment ID
            payment.circle_payment_id = circle_response["data"]["id"]
            db.commit()
            
            # Extract card payment details from Circle response
            card_details = None
            if "data" in circle_response and "paymentMethods" in circle_response["data"]:
                for method in circle_response["data"]["paymentMethods"]:
                    if method.get("type") == "card":
                        card_details = {
                            "payment_url": method.get("paymentUrl"),
                            "expires_at": method.get("expiresAt"),
                            "card_types": method.get("cardTypes", [])
                        }
                        break
            
            return {
                "payment_id": payment.id,
                "status": "pending",
                "payment_method": "credit_debit_card",
                "card_details": card_details,
                "message": "Please complete your payment using the provided payment link."
            }
            
        except Exception as e:
            logger.error(f"Error initiating card payment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initiate card payment"
            )
    
    async def process_circle_webhook(self, db: Session, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Circle webhook for payment status updates"""
        try:
            event_type = webhook_data.get("type")
            payment_data = webhook_data.get("data", {})
            circle_payment_id = payment_data.get("id")
            
            if not circle_payment_id:
                return {"status": "ignored", "reason": "No payment ID"}
            
            # Find payment by Circle payment ID
            payment = db.query(Payment).filter(Payment.circle_payment_id == circle_payment_id).first()
            if not payment:
                return {"status": "ignored", "reason": "Payment not found"}
            
            if event_type == "payment.successful":
                return await self._handle_successful_payment(db, payment, payment_data)
            elif event_type == "payment.failed":
                return await self._handle_failed_payment(db, payment, payment_data)
            else:
                return {"status": "ignored", "reason": f"Unhandled event type: {event_type}"}
                
        except Exception as e:
            logger.error(f"Error processing Circle webhook: {str(e)}")
            return {"status": "error", "reason": str(e)}
    
    async def _handle_successful_payment(self, db: Session, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment from Circle"""
        try:
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            # TODO: update deprecated utcnow method
            payment.updated_at = datetime.utcnow()
            
            # Get investment and project
            investment = db.query(Investment).filter(Investment.id == payment.investment_id).first()
            project = db.query(Project).filter(Project.id == investment.project_id).first()
            
            # Update investment status
            investment.payment_status = PaymentStatus.COMPLETED
            investment.transaction_id = payment_data.get("transactionId")
            
            # Update project raised amount
            project.current_raised += investment.amount
            
            # Process on-ramp and escrow transfer for card payments
            if payment.payment_method in ["card", "fiat"] and project.ieo_contract_address:
                try:
                    # Step 1: Convert EUR to USDC in Circle (ledger conversion)
                    conversion_result = await self.circle_client.convert_currency(
                        source_amount=str(int(payment.amount * 100)),  # Convert to cents
                        source_currency="EUR",
                        destination_currency="USDC"
                    )
                    
                    logger.info(f"Currency conversion EUR→USDC successful: {conversion_result}")
                    
                    # Step 3: Add escrow address to Circle Address Book (if not already added)
                    recipient_result = await self.circle_client.add_address_book_recipient(
                        address=project.ieo_contract_address,
                        chain="MATIC",  # Polygon
                        description=f"IEO for {project.name}"
                    )
                    
                    recipient_id = recipient_result["data"]["id"]
                    logger.info(f"Address book recipient created: {recipient_id}")
                    
                    # Step 4: Create crypto payout to escrow
                    # Note: You'll need to get your Circle Mint wallet ID from settings or API
                    source_wallet_id = settings.circle_mint_wallet_id  # Add this to config
                    
                    payout_result = await self.circle_client.create_crypto_payout(
                        amount=str(int(payment.amount * 100)),  # USDC amount in cents
                        currency="USDC",
                        recipient_id=recipient_id,
                        source_wallet_id=source_wallet_id
                    )
                    
                    payout_id = payout_result["data"]["id"]
                    payment.circle_transfer_id = payout_id
                    payment.crypto_payout_succeeded = True
                    
                    logger.info(f"USDC payout to IEO contract initiated: {payout_id}")

                    # Record the user's investment on-chain via admin function
                    try:
                        ieo_contract = blockchain_service.w3.eth.contract(
                            address=Web3.to_checksum_address(project.ieo_contract_address),
                            abi=IEO_ABI
                        )
                        usdc_amount_units = int(investment.amount * 1000000)  # USDC 6 decimals
                        gas_price = await blockchain_service.get_gas_price_with_safety_margin()
                        nonce = blockchain_service._get_nonce()
                        investor_checksum = Web3.to_checksum_address(payment.investor_wallet_address)
                        tx = ieo_contract.functions.adminRecordInvestment(investor_checksum, usdc_amount_units).build_transaction({
                            'from': blockchain_service.account.address,
                            'gasPrice': gas_price,
                            'nonce': nonce
                        })
                        gas_estimate = await blockchain_service.get_gas_limit_with_safety_margin(tx)
                        tx['gas'] = gas_estimate
                        tx_hash = await blockchain_service._send_transaction(tx, "Admin record investment")

                        # Mark recorded and create DB investment record (confirmed amounts)
                        payment.investment_recorded = True
                        investment.status = "confirmed"
                        investment.investment_time = datetime.utcnow()
                        investment.usdc_amount = investment.amount
                        # token_amount will be read from chain later by listener or can be calculated off-chain if needed
                        logger.info(f"Investment recorded on-chain: {tx_hash}")
                    except Exception as e:
                        logger.error(f"Failed to record investment on-chain: {e}")
                    
                except Exception as e:
                    logger.error(f"Failed to process on-ramp and IEO transfer: {str(e)}")
                    # Don't fail the payment, just log the error
                    # The transfer can be retried later
            
            db.commit()
            
            return {
                "status": "success",
                "payment_id": payment.id,
                "investment_id": investment.id,
                "circle_payout_id": payment.circle_transfer_id
            }
            
        except Exception as e:
            logger.error(f"Error handling successful payment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            return {"status": "error", "reason": str(e)}
    
    async def _handle_failed_payment(self, db: Session, payment: Payment, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment from Circle"""
        try:
            # Update payment status
            payment.status = PaymentStatus.FAILED
            payment.updated_at = datetime.utcnow()
            
            # Update investment status
            investment = db.query(Investment).filter(Investment.id == payment.investment_id).first()
            investment.payment_status = PaymentStatus.FAILED
            
            db.commit()
            
            return {
                "status": "failed",
                "payment_id": payment.id,
                "investment_id": investment.id
            }
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            return {"status": "error", "reason": str(e)}
    
    async def get_payment_status(self, db: Session, payment_id: str) -> Optional[Payment]:
        """Get payment status"""
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    async def get_user_investments(self, db: Session, user_id: str, skip: int = 0, limit: int = 100):
        """Get user's investment history"""
        return db.query(Investment).filter(Investment.user_id == user_id).offset(skip).limit(limit).all()
    
    async def close(self):
        """Close the Circle client"""
        await self.circle_client.close() 