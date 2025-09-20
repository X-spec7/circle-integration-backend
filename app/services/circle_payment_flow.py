"""
Circle Payment Flow Service
Handles the complete payment flow: Card Payment → EUR → EURC → USDC → Escrow
"""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from app.services.circle_client import CircleClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class CirclePaymentFlow:
    """Service for handling complete Circle payment flow"""
    
    def __init__(self):
        self.circle_client = CircleClient()
    
    async def process_card_payment_to_escrow(
        self,
        amount: Decimal,
        project_name: str,
        escrow_address: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Complete flow: Card Payment → EUR → EURC → USDC → Escrow
        
        Args:
            amount: Payment amount in EUR
            project_name: Name of the project
            escrow_address: Escrow contract address on Polygon
            project_id: Project ID for tracking
            
        Returns:
            Dict with payment flow results
        """
        try:
            logger.info(f"Starting payment flow for project {project_id}: {amount} EUR")
            
            # Step 1: Create card payment intent
            payment_intent = await self._create_card_payment_intent(amount, project_name)
            payment_id = payment_intent["data"]["id"]
            
            logger.info(f"Card payment intent created: {payment_id}")
            
            # Step 2: Wait for payment to be successful (this would be handled by webhook)
            # For now, we'll assume payment is successful and proceed with on-ramp
            
            # Step 3: Convert EURC to USDC (EUR is automatically converted to EURC)
            conversion_result = await self._convert_eurc_to_usdc(amount)
            conversion_id = conversion_result["data"]["id"]
            
            logger.info(f"Currency conversion initiated: {conversion_id}")
            
            # Step 4: Create USDC transfer to escrow (Circle Mint approach)
            transfer_result = await self._create_usdc_transfer_to_escrow(
                amount, escrow_address, project_id
            )
            transfer_id = transfer_result["data"]["id"]
            
            logger.info(f"USDC transfer to escrow initiated: {transfer_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "conversion_id": conversion_id,
                "transfer_id": transfer_id,
                "flow": "card_payment → eur → eurc → usdc → escrow (Circle Mint)"
            }
            
        except Exception as e:
            logger.error(f"Error in payment flow: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_card_payment_intent(self, amount: Decimal, description: str) -> Dict[str, Any]:
        """Create card payment intent"""
        try:
            return await self.circle_client.create_card_payment_intent(
                amount=str(int(amount * 100)),  # Convert to cents
                currency="EUR",
                description=description
            )
        except Exception as e:
            logger.error(f"Error creating card payment intent: {str(e)}")
            raise
    
    async def _convert_eurc_to_usdc(self, amount: Decimal) -> Dict[str, Any]:
        """Convert EURC to USDC in Circle Mint"""
        try:
            return await self.circle_client.convert_currency(
                source_amount=str(int(amount * 100)),  # Convert to cents
                source_currency="EURC",
                destination_currency="USDC"
            )
        except Exception as e:
            logger.error(f"Error converting EURC to USDC: {str(e)}")
            raise
    
    async def _add_escrow_to_address_book(self, escrow_address: str, project_name: str) -> Dict[str, Any]:
        """Add escrow address to Circle Address Book"""
        try:
            return await self.circle_client.add_address_book_recipient(
                address=escrow_address,
                chain="MATIC",  # Polygon
                description=f"Escrow for {project_name}"
            )
        except Exception as e:
            logger.error(f"Error adding escrow to address book: {str(e)}")
            raise
    
    async def _create_usdc_transfer_to_escrow(self, amount: Decimal, escrow_address: str, project_id: str) -> Dict[str, Any]:
        """Create USDC transfer from Circle Mint to escrow contract"""
        try:
            return await self.circle_client.create_mint_transfer(
                amount=str(int(amount * 100)),  # USDC amount in cents
                currency="USDC",
                escrow_address=escrow_address,
                project_id=project_id
            )
        except Exception as e:
            logger.error(f"Error creating USDC transfer to escrow: {str(e)}")
            raise
    
    async def get_payment_flow_status(
        self,
        payment_id: str = None,
        conversion_id: str = None,
        transfer_id: str = None
    ) -> Dict[str, Any]:
        """Get status of payment flow components"""
        try:
            status = {}
            
            if payment_id:
                payment_status = await self.circle_client.get_payment_status(payment_id)
                status["payment"] = payment_status["data"]
            
            if transfer_id:
                transfer_status = await self.circle_client.get_transfer_status(transfer_id)
                status["transfer"] = transfer_status["data"]
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting payment flow status: {str(e)}")
            return {"error": str(e)}
    
    async def get_business_account_info(self) -> Dict[str, Any]:
        """Get business account information and balances"""
        try:
            # Get bank details
            banks = await self.circle_client.get_business_account_banks()
            
            # Get balances
            balances = await self.circle_client.get_business_account_balance()
            
            return {
                "banks": banks["data"],
                "balances": balances["data"]
            }
            
        except Exception as e:
            logger.error(f"Error getting business account info: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the Circle client"""
        await self.circle_client.close() 