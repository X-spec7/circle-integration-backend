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
    
    async def create_payment_intent(self, amount: str, currency: str = "EUR", description: str = None) -> Dict[str, Any]:
        """Create a payment intent for fiat bank transfer (EUR)"""
        try:
            payload = {
                "amount": {"amount": amount, "currency": currency},
                "settlementCurrency": "EUR",
                "paymentMethods": [{"type": "sepaBankAccount"}],
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
    
    async def transfer_to_escrow(self, amount: str, currency: str, escrow_address: str, project_id: str) -> Dict[str, Any]:
        """Transfer EURC to on-chain escrow smart contract"""
        try:
            idempotency_key = str(uuid.uuid4())
            
            payload = {
                "idempotencyKey": idempotency_key,
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