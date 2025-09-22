from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.investment import InvestmentStatus

class InvestmentCreate(BaseModel):
    """Schema for creating an investment"""
    project_id: str = Field(..., description="Project ID to invest in")
    usdc_amount: Decimal = Field(..., gt=0, description="USDC amount to invest (6 decimals)")

class InvestmentResponse(BaseModel):
    """Schema for investment response"""
    id: str
    investor_id: str
    project_id: str
    project_name: str
    project_symbol: str
    usdc_amount: Decimal
    token_amount: Decimal
    investment_time: datetime
    status: InvestmentStatus
    claimed: bool
    refunded: bool
    claimable: bool
    refundable: bool
    claim_delay_hours: int
    refund_period_hours: int
    transaction_hash: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InvestmentListResponse(BaseModel):
    """Schema for investment list response"""
    items: List[InvestmentResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class InvestmentStats(BaseModel):
    """Schema for investment statistics"""
    total_investments: int
    total_usdc_invested: Decimal
    total_tokens_received: Decimal
    total_claimed: Decimal
    total_refunded: Decimal
    active_investments: int
    claimable_investments: int
    refundable_investments: int

class ClaimTokensRequest(BaseModel):
    """Schema for claiming tokens request"""
    project_id: Optional[str] = Field(None, description="Specific project ID to claim from (optional)")

class ClaimTokensResponse(BaseModel):
    """Schema for claiming tokens response"""
    project_id: str
    tokens_claimed: Decimal
    transaction_hash: str
    success: bool
    message: str

class RefundInvestmentRequest(BaseModel):
    """Schema for refunding investment request"""
    project_id: str = Field(..., description="Project ID")
    investment_index: Optional[int] = Field(None, description="Specific investment index to refund (optional)")

class RefundInvestmentResponse(BaseModel):
    """Schema for refunding investment response"""
    project_id: str
    usdc_refunded: Decimal
    transaction_hash: str
    success: bool
    message: str

class ProjectInvestmentInfo(BaseModel):
    """Schema for project investment information"""
    project_id: str
    project_name: str
    project_symbol: str
    is_ieo_active: bool
    min_investment: Decimal
    max_investment: Decimal
    total_raised: Decimal
    total_tokens_sold: Decimal
    user_investment_count: int
    user_total_invested: Decimal
    user_total_tokens: Decimal
    user_claimable_tokens: Decimal
    user_refundable_amount: Decimal
    claim_delay_hours: int
    refund_period_hours: int
    token_price: Optional[Decimal] = None
    price_timestamp: Optional[datetime] = None
