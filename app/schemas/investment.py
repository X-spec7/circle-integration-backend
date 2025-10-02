from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.investment import InvestmentStatus, PaymentMethod
from decimal import Decimal

class InvestmentCreate(BaseModel):
    project_id: str = Field(..., description="ID of the project to invest in")
    amount: int = Field(..., gt=0, description="Investment amount in USDC (6 decimals)")
    payment_method: PaymentMethod = Field(..., description="Payment method for the investment")

class InvestmentResponse(BaseModel):
    id: str
    investor_id: str
    project_id: str
    amount: int
    status: InvestmentStatus
    payment_method: PaymentMethod
    created_at: datetime
    updated_at: datetime
    investor_wallet_address: Optional[str] = None
    block_number: Optional[int] = None

    class Config:
        from_attributes = True

class InvestmentDetail(BaseModel):
    id: str
    investor_id: str
    project_id: str
    amount: int
    status: InvestmentStatus
    payment_method: PaymentMethod
    created_at: datetime
    updated_at: datetime
    project_name: str
    project_symbol: str
    project_status: str
    tokens_allocated: Optional[int] = None
    claimable_tokens: Optional[int] = None
    refund_amount: Optional[int] = None

    class Config:
        from_attributes = True

class InvestmentListResponse(BaseModel):
    investments: List[InvestmentResponse]
    total: int
    page: int
    per_page: int

class InvestmentStats(BaseModel):
    total_investments: int
    total_amount: int
    active_investments: int
    completed_investments: int
    pending_investments: int

class ClaimTokensRequest(BaseModel):
    investment_id: str

class RefundInvestmentRequest(BaseModel):
    investment_id: str

class ClaimTokensResponse(BaseModel):
    success: bool
    transaction_hash: Optional[str] = None
    message: str

class RefundInvestmentResponse(BaseModel):
    success: bool
    transaction_hash: Optional[str] = None
    message: str

class ProjectInvestmentInfo(BaseModel):
    project_id: str
    project_name: str
    total_investments: int
    total_amount: int
    unique_investors: int
    average_investment: float
