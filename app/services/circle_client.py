import httpx
import os
import uuid
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CircleClient:
    """Circle API client for handling payments and transfers"""
    
    def __init__(self):
        self.api_key = settings.circle_api_key
        self.base_url = settings.circle_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )
    
    async def create_payment_intent(self, amount: str, currency: str = "EUR", description: str = None, payment_method: str = "sepaBankAccount") -> Dict[str, Any]:
        """Create a payment intent for fiat payment (SEPA or Card)"""
        try:
            # Validate payment method
            valid_methods = ["sepaBankAccount", "card"]
            if payment_method not in valid_methods:
                raise ValueError(f"Invalid payment method. Must be one of: {valid_methods}")
            
            payload = {
                "amount": {"amount": amount, "currency": currency},
                "settlementCurrency": "EUR",
                "paymentMethods": [{"type": payment_method}],
                "description": description or "Token Investment Payment"
            }
            
            response = await self.client.post("/payments", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error creating payment intent: {e.response.text}")
            raise Exception(f"Failed to create payment intent: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {str(e)}")
            raise
    
    async def create_card_payment_intent(self, amount: str, currency: str = "EUR", description: str = None) -> Dict[str, Any]:
        """Create a payment intent for credit/debit card payment"""
        try:
            payload = {
                "amount": {"amount": amount, "currency": currency},
                "settlementCurrency": "EUR",
                "paymentMethods": [{"type": "card"}],
                "description": description or "Token Investment Payment"
            }
            
            response = await self.client.post("/payments", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error creating card payment intent: {e.response.text}")
            raise Exception(f"Failed to create card payment intent: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating card payment intent: {str(e)}")
            raise
    
    async def create_multi_payment_intent(self, amount: str, currency: str = "EUR", description: str = None) -> Dict[str, Any]:
        """Create a payment intent with multiple payment methods (SEPA + Card)"""
        try:
            payload = {
                "amount": {"amount": amount, "currency": currency},
                "settlementCurrency": "EUR",
                "paymentMethods": [
                    {"type": "sepaBankAccount"},
                    {"type": "card"}
                ],
                "description": description or "Token Investment Payment"
            }
            
            response = await self.client.post("/payments", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error creating multi-payment intent: {e.response.text}")
            raise Exception(f"Failed to create multi-payment intent: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating multi-payment intent: {str(e)}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status from Circle"""
        try:
            response = await self.client.get(f"/payments/{payment_id}")
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting payment status: {e.response.text}")
            raise Exception(f"Failed to get payment status: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting payment status: {str(e)}")
            raise

    # New methods for proper Circle Mint flow
    
    async def get_business_account_banks(self) -> Dict[str, Any]:
        """Get business account bank details for SEPA deposits"""
        try:
            response = await self.client.get("/businessAccount/banks/wire")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting business account banks: {e.response.text}")
            raise Exception(f"Failed to get business account banks: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting business account banks: {str(e)}")
            raise

    async def convert_currency(self, source_amount: str, source_currency: str, destination_currency: str) -> Dict[str, Any]:
        """Convert currency in Circle Mint (e.g., EURC to USDC)"""
        try:
            payload = {
                "source": {"amount": source_amount, "currency": source_currency},
                "destination": {"currency": destination_currency}
            }
            
            response = await self.client.post("/conversions", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error converting currency: {e.response.text}")
            raise Exception(f"Failed to convert currency: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error converting currency: {str(e)}")
            raise

    async def add_address_book_recipient(self, address: str, chain: str = "MATIC", description: str = None) -> Dict[str, Any]:
        """Add escrow address to Circle Address Book"""
        try:
            payload = {
                "idempotencyKey": str(uuid.uuid4()),
                "chain": chain,
                "address": address,
                "description": description or "Project Escrow Contract"
            }
            
            response = await self.client.post("/addressBook/recipients", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error adding address book recipient: {e.response.text}")
            raise Exception(f"Failed to add address book recipient: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error adding address book recipient: {str(e)}")
            raise

    async def get_address_book_recipient(self, recipient_id: str) -> Dict[str, Any]:
        """Get address book recipient status"""
        try:
            response = await self.client.get(f"/addressBook/recipients/{recipient_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting address book recipient: {e.response.text}")
            raise Exception(f"Failed to get address book recipient: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting address book recipient: {str(e)}")
            raise

    async def create_crypto_payout(self, amount: str, currency: str, recipient_id: str, source_wallet_id: str) -> Dict[str, Any]:
        """Create crypto payout to escrow contract"""
        try:
            payload = {
                "idempotencyKey": str(uuid.uuid4()),
                "source": {"type": "wallet", "id": source_wallet_id},
                "destination": {
                    "type": "address_book_recipient",
                    "id": recipient_id
                },
                "amount": {"amount": amount, "currency": currency}
            }
            
            response = await self.client.post("/payouts", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error creating crypto payout: {e.response.text}")
            raise Exception(f"Failed to create crypto payout: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating crypto payout: {str(e)}")
            raise

    async def get_payout_status(self, payout_id: str) -> Dict[str, Any]:
        """Get payout status"""
        try:
            response = await self.client.get(f"/payouts/{payout_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting payout status: {e.response.text}")
            raise Exception(f"Failed to get payout status: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting payout status: {str(e)}")
            raise

    async def get_business_account_balance(self) -> Dict[str, Any]:
        """Get business account balance (Circle Mint)"""
        try:
            response = await self.client.get("/businessAccount/balances")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting business account balance: {e.response.text}")
            raise Exception(f"Failed to get business account balance: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting business account balance: {str(e)}")
            raise

    async def get_all_wallets(self) -> Dict[str, Any]:
        """Get all wallets from Circle"""
        try:
            response = await self.client.get("/wallets")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting wallets: {e.response.text}")
            raise Exception(f"Failed to get wallets: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting wallets: {str(e)}")
            raise

    # Legacy methods (keeping for backward compatibility)
    
    async def transfer_to_escrow(self, amount: str, currency: str, escrow_address: str, project_id: str) -> Dict[str, Any]:
        """Transfer from Circle Mint business account to on-chain escrow smart contract"""
        try:
            idempotency_key = str(uuid.uuid4())
            
            payload = {
                "idempotencyKey": idempotency_key,
                "source": {
                    "type": "wallet",
                    "id": "primary"  # Circle Mint business account
                },
                "destination": {
                    "type": "blockchain",
                    "address": escrow_address,
                    "chain": "MATIC"  # Polygon
                },
                "amount": {"amount": amount, "currency": currency},
                "metadata": {
                    "project_id": project_id,
                    "transfer_type": "escrow_deposit"
                }
            }
            
            response = await self.client.post("/transfers", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error transferring to escrow: {e.response.text}")
            raise Exception(f"Failed to transfer to escrow: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error transferring to escrow: {str(e)}")
            raise
    
    async def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Get transfer status from Circle"""
        try:
            response = await self.client.get(f"/transfers/{transfer_id}")
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting transfer status: {e.response.text}")
            raise Exception(f"Failed to get transfer status: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting transfer status: {str(e)}")
            raise

    async def create_mint_transfer(self, amount: str, currency: str, escrow_address: str, project_id: str) -> Dict[str, Any]:
        """Create transfer from Circle Mint business account to blockchain address"""
        try:
            idempotency_key = str(uuid.uuid4())
            
            payload = {
                "idempotencyKey": idempotency_key,
                "source": {
                    "type": "wallet",
                    "id": "primary"  # Circle Mint business account
                },
                "destination": {
                    "type": "blockchain",
                    "address": escrow_address,
                    "chain": "MATIC"  # Polygon
                },
                "amount": {"amount": amount, "currency": currency},
                "metadata": {
                    "project_id": project_id,
                    "transfer_type": "escrow_deposit"
                }
            }
            
            response = await self.client.post("/transfers", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error creating mint transfer: {e.response.text}")
            raise Exception(f"Failed to create mint transfer: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating mint transfer: {str(e)}")
            raise
    
    async def create_wallet(self, description: str = None) -> Dict[str, Any]:
        """Create a new wallet for a project"""
        try:
            payload = {
                "description": description or "Project Escrow Wallet"
            }
            
            response = await self.client.post("/wallets", json=payload)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error creating wallet: {e.response.text}")
            raise Exception(f"Failed to create wallet: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating wallet: {str(e)}")
            raise
    
    async def get_wallet_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet balance"""
        try:
            response = await self.client.get(f"/wallets/{wallet_id}")
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Circle API error getting wallet balance: {e.response.text}")
            raise Exception(f"Failed to get wallet balance: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error getting wallet balance: {str(e)}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 