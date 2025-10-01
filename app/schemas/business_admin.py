from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class StartIEORequest(BaseModel):
    """Schema for starting IEO"""
    price_oracle_address: Optional[str] = Field(None, description="Price oracle contract address")

class EndIEORequest(BaseModel):
    """Schema for ending IEO"""
    reason: Optional[str] = Field(None, description="Reason for ending IEO")

class IEOStatusResponse(BaseModel):
    """Schema for IEO status response"""
    project_id: str
    is_active: bool
    is_paused: bool
    start_time: Optional[datetime] = None
    total_raised: Decimal
    total_tokens_sold: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal
    withdrawable_amount: Decimal
    investment_count: int
    investor_count: int
    min_investment: Decimal
    max_investment: Decimal
    claim_delay_hours: int
    refund_period_hours: int
    withdrawal_delay_hours: int

class WithdrawUSDCRequest(BaseModel):
    """Schema for withdrawing specific USDC amount"""
    amount: Decimal = Field(..., gt=0, description="USDC amount to withdraw (6 decimals)")

class WithdrawAllUSDCRequest(BaseModel):
    """Schema for withdrawing all available USDC"""
    pass

class WithdrawalResponse(BaseModel):
    """Schema for withdrawal response"""
    project_id: str
    amount_withdrawn: Decimal
    transaction_hash: str
    success: bool
    message: str
    remaining_balance: Decimal

class ProjectStatsResponse(BaseModel):
    """Schema for project statistics response"""
    project_id: str
    project_name: str
    project_symbol: str
    total_raised: Decimal
    total_tokens_sold: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal
    withdrawable_amount: Decimal
    investment_count: int
    unique_investors: int
    average_investment: Decimal
    largest_investment: Decimal
    smallest_investment: Decimal
    is_ieo_active: bool
    is_paused: bool
    start_time: Optional[datetime] = None
    created_at: datetime

class WhitelistUserRequest(BaseModel):
    """Schema for whitelisting a single user"""
    wallet_address: str = Field(..., description="User wallet address to whitelist")

class WhitelistBatchRequest(BaseModel):
    """Schema for batch whitelisting users"""
    wallet_addresses: List[str] = Field(..., min_items=1, max_items=100, description="List of wallet addresses to whitelist")

class WhitelistResponse(BaseModel):
    """Schema for whitelist operation response"""
    project_id: str
    operation: str  # "add", "remove", "batch_add", "batch_remove"
    wallet_addresses: List[str]
    transaction_hash: str
    success: bool
    message: str

class WhitelistListResponse(BaseModel):
    """Schema for whitelist list response"""
    project_id: str
    whitelisted_addresses: List[str]
    total_count: int
    page: int
    limit: int
    total_pages: int

class CircuitBreakerSettings(BaseModel):
    """Schema for circuit breaker settings"""
    enabled: bool
    triggered: bool
    price_staleness_threshold: int  # seconds
    max_price_deviation: int  # basis points
    last_valid_price: Decimal
    price_timestamp: Optional[datetime] = None

class PriceValidationSettings(BaseModel):
    """Schema for price validation settings"""
    min_token_price: Decimal
    max_token_price: Decimal
    price_oracle_address: str
    circuit_breaker: CircuitBreakerSettings

# New schemas for listing business admin projects
class BusinessAdminProjectSummary(BaseModel):
    id: str
    name: str
    symbol: str
    status: str
    owner_id: str
    category: Optional[str] = None
    initial_supply: Optional[int] = None
    current_raised: Optional[Decimal] = None
    business_admin_wallet: Optional[str] = None
    token_contract_address: Optional[str] = None
    ieo_contract_address: Optional[str] = None
    reward_tracking_contract_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    has_whitelist_request: Optional[bool] = False

class BusinessAdminProjectListResponse(BaseModel):
    items: List[BusinessAdminProjectSummary]
    total: int
    page: int
    limit: int
    total_pages: int

# New schemas for whitelist requests flow
class InvestorWhitelistApplyRequest(BaseModel):
    project_id: str
    addresses: List[str] = Field(..., min_items=1, max_items=20)

class InvestorWhitelistApplyResponse(BaseModel):
    request_id: str
    project_id: str
    addresses: List[str]
    status: str
    created_at: datetime

class WhitelistRequestItem(BaseModel):
    id: str
    investor_id: str
    applicant_name: Optional[str] = None
    addresses: List[str]
    status: str
    created_at: datetime

class WhitelistRequestListResponse(BaseModel):
    items: List[WhitelistRequestItem]
    total: int

class BusinessAdminProjectDetailResponse(BaseModel):
    id: str
    name: str
    symbol: str
    status: str
    category: Optional[str] = None
    owner_id: str
    initial_supply: Optional[int] = None
    current_raised: Optional[Decimal] = None
    business_admin_wallet: Optional[str] = None
    token_contract_address: Optional[str] = None
    ieo_contract_address: Optional[str] = None
    reward_tracking_contract_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    has_whitelist_request: bool
    pending_whitelist_requests: List[WhitelistRequestItem]

# Request/Response for setting oracle address (owner-only)
class SetOracleRequest(BaseModel):
    oracle_address: str = Field(..., description="Oracle contract address")

class SetOracleResponse(BaseModel):
    project_id: str
    oracle_address: str
    transaction_hash: str
    message: str
