from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from app.models.investment import Investment, PaymentMethod, PaymentStatus
from app.models.payment import Payment
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.services.circle_client import CircleClient
from app.services.blockchain_service import blockchain_service
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
            
            # Create investment record
            investment = Investment(
                id=str(uuid.uuid4()),
                user_id=user.id,
                project_id=project.id,
                amount=payment_data.amount,
                payment_status=PaymentStatus.PENDING
            )
            
            db.add(investment)
            db.commit()
            db.refresh(investment)
            
            # Initiate payment based on method
            if payment_data.payment_method == "fiat":
                return await self._initiate_fiat_payment(db, investment, project)
            elif payment_data.payment_method == "card":
                return await self._initiate_card_payment(db, investment, project)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payment method. Supported: 'fiat' (SEPA) or 'card' (credit/debit)"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initiate payment"
            )
    
    async def _initiate_fiat_payment(self, db: Session, investment: Investment, project: Project) -> Dict[str, Any]:
        """Initiate fiat payment through Circle (SEPA Bank Transfer)"""
        try:
            # Create payment record
            payment = Payment(
                id=str(uuid.uuid4()),
                investment_id=investment.id,
                amount=investment.amount,
                currency="EUR",
                payment_method="fiat",
                status=PaymentStatus.PENDING
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            # Create Circle payment intent for SEPA
            description = f"Investment in {project.name} - {investment.amount} EUR"
            circle_response = await self.circle_client.create_payment_intent(
                amount=str(int(investment.amount * 100)),  # Convert to cents
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
    
    async def _initiate_card_payment(self, db: Session, investment: Investment, project: Project) -> Dict[str, Any]:
        """Initiate card payment through Circle"""
        try:
            # Create payment record
            payment = Payment(
                id=str(uuid.uuid4()),
                investment_id=investment.id,
                amount=investment.amount,
                currency="EUR",
                payment_method="card",
                status=PaymentStatus.PENDING
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            # Create Circle payment intent for card
            description = f"Investment in {project.name} - {investment.amount} EUR"
            circle_response = await self.circle_client.create_payment_intent(
                amount=str(int(investment.amount * 100)),  # Convert to cents
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
            if payment.payment_method in ["card", "fiat"] and project.escrow_contract_address:
                try:
                    # Step 1: EUR is automatically converted to EURC in Circle Mint
                    # Step 2: Convert EURC to USDC (since EURC is not available on Polygon)
                    conversion_result = await self.circle_client.convert_currency(
                        source_amount=str(int(payment.amount * 100)),  # Convert to cents
                        source_currency="EURC",
                        destination_currency="USDC"
                    )
                    
                    logger.info(f"Currency conversion successful: {conversion_result}")
                    
                    # Step 3: Add escrow address to Circle Address Book (if not already added)
                    recipient_result = await self.circle_client.add_address_book_recipient(
                        address=project.escrow_contract_address,
                        chain="MATIC",  # Polygon
                        description=f"Escrow for {project.name}"
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
                    
                    logger.info(f"USDC payout to escrow initiated: {payout_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process on-ramp and escrow transfer: {str(e)}")
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