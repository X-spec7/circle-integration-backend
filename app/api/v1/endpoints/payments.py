from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import hmac
import hashlib
import json
import base64
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import httpx

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.investment import Investment
from app.services.payment_service import PaymentService
from app.schemas.payment import (
    InvestmentCreate, InvestmentResponse, PaymentInitiateRequest, 
    PaymentInitiateResponse, PaymentStatusResponse, CircleWebhookData,
    PaymentConfirmRequest, CryptoPaymentRequest, CryptoPaymentResponse
)
from app.core.config import settings

router = APIRouter()

@router.post("/investments", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new investment in a project
    """
    payment_service = PaymentService()
    try:
        investment = await payment_service.create_investment(db, current_user, investment_data)
        return investment
    finally:
        await payment_service.close()

@router.post("/payments/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    payment_data: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate payment process for investment
    
    Payment Methods:
    - "fiat": SEPA Bank Transfer (lower fees, 1-3 days)
    - "card": Credit/Debit Card (instant, higher fees)
    """
    payment_service = PaymentService()
    try:
        result = await payment_service.initiate_payment(db, current_user, payment_data)
        return PaymentInitiateResponse(**result)
    finally:
        await payment_service.close()

# NOTE: not used anymore
@router.post("/payments/crypto", response_model=CryptoPaymentResponse)
async def initiate_crypto_payment(
    crypto_data: CryptoPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate crypto payment for investment
    """
    payment_service = PaymentService()
    try:
        # Create payment request
        payment_data = PaymentInitiateRequest(
            project_id=crypto_data.project_id,
            amount=crypto_data.amount,
            payment_method="crypto"
        )
        
        result = await payment_service.initiate_payment(db, current_user, payment_data)
        
        # Add crypto-specific details
        result["escrow_address"] = result.get("escrow_address", settings.escrow_wallet_address)
        result["currency"] = crypto_data.currency
        
        return CryptoPaymentResponse(**result)
    finally:
        await payment_service.close()

@router.get("/payments/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment status
    """
    payment_service = PaymentService()
    try:
        payment = await payment_service.get_payment_status(db, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check if user owns this payment
        investment = db.query(Investment).filter(Investment.id == payment.investment_id).first()
        if investment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this payment"
            )
        
        return payment
    finally:
        await payment_service.close()

@router.post("/payments/confirm")
async def confirm_payment(
    confirm_data: PaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm payment completion (for crypto payments)
    """
    payment_service = PaymentService()
    try:
        payment = await payment_service.get_payment_status(db, confirm_data.payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check if user owns this payment
        investment = db.query(Investment).filter(Investment.id == payment.investment_id).first()
        if investment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to confirm this payment"
            )
        
        # Update payment with transaction hash
        if confirm_data.transaction_id:
            payment.transaction_hash = confirm_data.transaction_id
            payment.status = "processing"
            db.commit()
        
        return {"message": "Payment confirmation received", "status": "processing"}
    finally:
        await payment_service.close()

@router.get("/investments", response_model=List[InvestmentResponse])
async def get_user_investments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's investment history
    """
    payment_service = PaymentService()
    try:
        investments = await payment_service.get_user_investments(db, current_user.id, skip, limit)
        return investments
    finally:
        await payment_service.close()

@router.get("/investments/{investment_id}", response_model=InvestmentResponse)
async def get_investment_details(
    investment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific investment details
    """
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    if investment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this investment"
        )
    
    return investment

# Circle Webhook endpoint
@router.head("/webhooks/circle")
async def circle_webhook_head():
    """
    Handle Circle webhook HEAD requests for endpoint validation
    """
    return {"status": "ok"}

@router.post("/webhooks/circle")
async def circle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Circle webhooks for payment status updates
    """
    try:
        # Get the raw body
        body = await request.body()
        
        # Verify webhook signature using Circle's ECDSA method
        if settings.circle_api_key:
            signature = request.headers.get("X-Circle-Signature")
            key_id = request.headers.get("X-Circle-Key-Id")
            
            if not signature or not key_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing signature or key ID"
                )
            
            # Verify signature using Circle's public key
            if not await verify_circle_signature(signature, key_id, body):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid signature"
                )
        
        # Parse webhook data
        webhook_data = json.loads(body)
        
        # Process webhook
        payment_service = PaymentService()
        try:
            result = await payment_service.process_circle_webhook(db, webhook_data)
            return result
        finally:
            await payment_service.close()
            
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing error: {str(e)}"
        )

async def verify_circle_signature(signature: str, key_id: str, body: bytes) -> bool:
    """
    Verify Circle webhook signature using their public key
    """
    try:
        # Get the public key from Circle
        public_key_data = await get_circle_public_key(key_id)
        if not public_key_data:
            return False
        
        # Decode the public key
        public_key_bytes = base64.b64decode(public_key_data["publicKey"])
        public_key = serialization.load_der_public_key(public_key_bytes)
        
        # Decode the signature
        signature_bytes = base64.b64decode(signature)
        
        # Verify the signature
        public_key.verify(
            signature_bytes,
            body,
            ec.ECDSA(hashes.SHA256()),
        )
        return True
        
    except (InvalidSignature, Exception) as e:
        print(f"Signature verification failed: {str(e)}")
        return False

# Cache for Circle public keys to avoid repeated API calls
_circle_public_keys_cache = {}

async def get_circle_public_key(key_id: str) -> dict:
    """
    Retrieve public key from Circle API with caching
    """
    # Check cache first
    if key_id in _circle_public_keys_cache:
        return _circle_public_keys_cache[key_id]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.circle.com/v2/notifications/publicKey/{key_id}",
                headers={
                    "Authorization": f"Bearer {settings.circle_api_key}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            public_key_data = response.json()["data"]
            
            # Cache the public key
            _circle_public_keys_cache[key_id] = public_key_data
            return public_key_data
    except Exception as e:
        print(f"Failed to get Circle public key: {str(e)}")
        return None 