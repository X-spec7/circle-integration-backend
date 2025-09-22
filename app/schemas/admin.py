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
    user_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    user_type: Optional[str] = None

class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total: int
    page: int
    per_page: int

class AdminProjectResponse(BaseModel):
    id: str
    name: str
    symbol: str
    description: str
    category: str
    status: str
    initial_supply: int
    min_investment: int
    max_investment: int
    delay_days: int
    business_admin_wallet: str
    token_contract_address: Optional[str] = None
    ieo_contract_address: Optional[str] = None
    reward_tracking_contract_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AdminProjectUpdate(BaseModel):
    status: Optional[str] = None
    business_admin_wallet: Optional[str] = None

class AdminProjectListResponse(BaseModel):
    projects: List[AdminProjectResponse]
    total: int
    page: int
    per_page: int

class AdminDashboardStats(BaseModel):
    total_users: int
    total_projects: int
    active_projects: int
    total_investments: int
    total_volume: int

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
    is_active: Optional[bool] = None
    search: Optional[str] = None

class AdminProjectFilters(BaseModel):
    status: Optional[str] = None
    category: Optional[str] = None
    search: Optional[str] = None

class AdminActionLog(BaseModel):
    id: str
    admin_id: str
    action_type: str
    target_type: str  # "user", "project", "investment"
    target_id: str
    details: dict
    created_at: datetime

    class Config:
        from_attributes = True
