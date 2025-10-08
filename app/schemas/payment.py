from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.investment import PaymentMethod, PaymentStatus

class InvestmentCreate(BaseModel):
    """Schema for creating a new investment"""
    project_id: str = Field(..., description="Project ID to invest in")
    amount: Decimal = Field(..., gt=0, description="Investment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method (crypto or fiat)")
    currency: str = Field(default="EUR", description="Currency for payment")

class InvestmentResponse(BaseModel):
    """Schema for investment response"""
    id: str
    user_id: str
    project_id: str
    amount: Decimal
    tokens_received: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentInitiateRequest(BaseModel):
    """Schema for initiating payment"""
    project_id: str = Field(..., description="Project ID")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    investor_wallet_address: str = Field(..., description="Investor wallet (must be whitelisted)")

class PaymentInitiateResponse(BaseModel):
    """Schema for payment initiation response"""
    payment_id: str
    status: str
    payment_url: Optional[str] = None
    bank_details: Optional[dict] = None
    message: str
    payment_id: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    """Schema for payment status response"""
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    transaction_hash: Optional[str] = None
    circle_payment_id: Optional[str] = None
    circle_transfer_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CircleWebhookData(BaseModel):
    """Schema for Circle webhook data"""
    type: str
    data: dict
    timestamp: str

class PaymentConfirmRequest(BaseModel):
    """Schema for confirming payment"""
    payment_id: str = Field(..., description="Payment ID")
    transaction_id: Optional[str] = Field(None, description="Transaction hash (for crypto payments)")

class CryptoPaymentRequest(BaseModel):
    """Schema for crypto payment request"""
    project_id: str = Field(..., description="Project ID")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    wallet_address: str = Field(..., description="Investor's wallet address")
    currency: str = Field(default="USDC", description="Crypto currency")

class CryptoPaymentResponse(BaseModel):
    """Schema for crypto payment response"""
    payment_id: str
    escrow_address: str
    amount: Decimal
    currency: str
    message: str 