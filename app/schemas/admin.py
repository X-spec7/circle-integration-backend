from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import re

class WhitelistAddRequest(BaseModel):
    address: str = Field(..., description="Ethereum address to add to whitelist")
    
    @validator('address')
    def validate_address(cls, v):
        if not re.match(r"^0x[a-fA-F0-9]{40}$", v):
            raise ValueError("Invalid Ethereum address format")
        return v

class WhitelistRemoveRequest(BaseModel):
    address: str = Field(..., description="Ethereum address to remove from whitelist")
    
    @validator('address')
    def validate_address(cls, v):
        if not re.match(r"^0x[a-fA-F0-9]{40}$", v):
            raise ValueError("Invalid Ethereum address format")
        return v

class WhitelistResponse(BaseModel):
    project_id: str
    address: str
    action: str  # "added" or "removed"
    transaction_hash: str
    message: str

class AdminUserResponse(BaseModel):
    id: str
    email: str
    username: str
    name: str
    user_type: str
    company: Optional[str] = None
    status: str
    is_active: bool
    is_verified: bool
    wallet_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    project_count: int
    investment_count: int

    class Config:
        from_attributes = True

class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    user_type: Optional[str] = None
    status: Optional[str] = None

class AdminUserListResponse(BaseModel):
    items: List[AdminUserResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class AdminProjectResponse(BaseModel):
    id: str
    owner_id: str
    owner_name: str
    owner_email: str
    owner_company: Optional[str] = None
    name: str
    symbol: str
    description: str
    category: str
    initial_supply: int
    current_raised: int
    risk_level: str
    status: str
    image_url: Optional[str] = None
    business_plan_url: Optional[str] = None
    whitepaper_url: Optional[str] = None
    delay_days: int
    min_investment: int
    max_investment: int
    business_admin_wallet: str
    token_contract_address: Optional[str] = None
    ieo_contract_address: Optional[str] = None
    reward_tracking_contract_address: Optional[str] = None
    token_deployment_tx: Optional[str] = None
    ieo_deployment_tx: Optional[str] = None
    reward_tracking_deployment_tx: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    investment_count: int
    total_investors: int

    class Config:
        from_attributes = True

class AdminProjectUpdate(BaseModel):
    status: Optional[str] = None
    business_admin_wallet: Optional[str] = None
    risk_level: Optional[str] = None
    category: Optional[str] = None

class AdminProjectListResponse(BaseModel):
    items: List[AdminProjectResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class AdminDashboardStats(BaseModel):
    total_users: int
    total_smes: int
    total_investors: int
    total_projects: int
    active_projects: int
    pending_projects: int
    completed_projects: int
    rejected_projects: int
    total_raised: int
    total_investments: int
    recent_users: List[AdminUserResponse]
    recent_projects: List[AdminProjectResponse]

class BusinessAdminUpdate(BaseModel):
    business_admin_wallet: str

class BusinessAdminUpdateResponse(BaseModel):
    project_id: str
    old_business_admin_wallet: str
    new_business_admin_wallet: str
    transaction_hash: str
    message: str

class AdminUserFilters(BaseModel):
    user_type: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None

class AdminProjectFilters(BaseModel):
    status: Optional[str] = None
    search: Optional[str] = None
    risk_level: Optional[str] = None
    category: Optional[str] = None

class AdminActionLog(BaseModel):
    id: str
    admin_id: str
    action: str
    target_type: str
    target_id: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
