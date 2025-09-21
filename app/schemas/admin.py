from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.user import UserType, UserStatus
from app.models.project import ProjectStatus, RiskLevel

# Admin User Management Schemas
class AdminUserResponse(BaseModel):
    """Admin view of user data"""
    id: str
    email: str
    username: str
    name: str
    user_type: UserType
    company: Optional[str] = None
    status: UserStatus
    is_active: bool
    is_verified: bool
    wallet_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    project_count: Optional[int] = 0
    investment_count: Optional[int] = 0

    class Config:
        from_attributes = True

class AdminUserUpdate(BaseModel):
    """Schema for admin to update user"""
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    company: Optional[str] = Field(None, max_length=255)

class AdminUserListResponse(BaseModel):
    """Paginated list of users for admin"""
    items: List[AdminUserResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# Admin Project Management Schemas
class AdminProjectResponse(BaseModel):
    """Admin view of project data with additional details"""
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
    current_raised: Optional[Decimal] = None
    end_date: datetime
    risk_level: RiskLevel
    status: ProjectStatus
    image_url: Optional[str] = None
    business_plan_url: Optional[str] = None
    whitepaper_url: Optional[str] = None
    delay_days: int
    min_investment: int
    max_investment: int
    token_contract_address: Optional[str] = None
    ieo_contract_address: Optional[str] = None
    reward_tracking_contract_address: Optional[str] = None
    token_deployment_tx: Optional[str] = None
    ieo_deployment_tx: Optional[str] = None
    reward_tracking_deployment_tx: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    investment_count: Optional[int] = 0
    total_investors: Optional[int] = 0

    class Config:
        from_attributes = True

class AdminProjectUpdate(BaseModel):
    """Schema for admin to update project"""
    status: Optional[ProjectStatus] = None
    risk_level: Optional[RiskLevel] = None
    business_admin_wallet: Optional[str] = Field(None, description="New business admin wallet address")

class AdminProjectListResponse(BaseModel):
    """Paginated list of projects for admin"""
    items: List[AdminProjectResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# Admin Dashboard Schemas
class AdminDashboardStats(BaseModel):
    """Admin dashboard statistics"""
    total_users: int
    total_smes: int
    total_investors: int
    total_projects: int
    active_projects: int
    pending_projects: int
    completed_projects: int
    rejected_projects: int
    total_raised: Decimal
    total_investments: int
    recent_users: List[AdminUserResponse]
    recent_projects: List[AdminProjectResponse]

# Business Admin Management Schemas
class BusinessAdminUpdate(BaseModel):
    """Schema for updating business admin wallet in smart contracts"""
    project_id: str
    new_business_admin_wallet: str = Field(..., description="New business admin wallet address")

class BusinessAdminUpdateResponse(BaseModel):
    """Response after updating business admin"""
    project_id: str
    old_business_admin: str
    new_business_admin: str
    transaction_hash: str
    success: bool
    message: str

# Admin Filters
class AdminUserFilters(BaseModel):
    """Filters for admin user queries"""
    user_type: Optional[UserType] = None
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search in name, email, username, company")
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None

class AdminProjectFilters(BaseModel):
    """Filters for admin project queries"""
    status: Optional[ProjectStatus] = None
    risk_level: Optional[RiskLevel] = None
    category: Optional[str] = None
    owner_id: Optional[str] = None
    search: Optional[str] = Field(None, description="Search in name, symbol, description")
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    raised_min: Optional[Decimal] = None
    raised_max: Optional[Decimal] = None

# System Management Schemas
class SystemSettings(BaseModel):
    """System-wide settings"""
    maintenance_mode: bool = False
    new_user_registration: bool = True
    new_project_creation: bool = True
    min_investment_amount: int = 100
    max_investment_amount: int = 1000000
    default_delay_days: int = 7

class SystemSettingsUpdate(BaseModel):
    """Schema for updating system settings"""
    maintenance_mode: Optional[bool] = None
    new_user_registration: Optional[bool] = None
    new_project_creation: Optional[bool] = None
    min_investment_amount: Optional[int] = Field(None, ge=1)
    max_investment_amount: Optional[int] = Field(None, ge=1000)
    default_delay_days: Optional[int] = Field(None, ge=1, le=365)

# Audit Log Schemas
class AdminActionLog(BaseModel):
    """Log of admin actions"""
    id: str
    admin_id: str
    admin_name: str
    action: str
    target_type: str  # 'user', 'project', 'system'
    target_id: Optional[str] = None
    details: dict
    timestamp: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True

class AdminActionLogResponse(BaseModel):
    """Paginated admin action logs"""
    items: List[AdminActionLog]
    total: int
    page: int
    limit: int
    total_pages: int
