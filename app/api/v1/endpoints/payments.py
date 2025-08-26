from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import hmac
import hashlib
import json

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
    """
    payment_service = PaymentService()
    try:
        result = await payment_service.initiate_payment(db, current_user, payment_data)
        return PaymentInitiateResponse(**result)
    finally:
        await payment_service.close()

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
        
        # Verify webhook signature (if webhook secret is configured)
        if settings.circle_webhook_secret:
            signature = request.headers.get("circle-signature")
            if not signature:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing signature"
                )
            
            # Verify signature
            expected_signature = hmac.new(
                settings.circle_webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
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