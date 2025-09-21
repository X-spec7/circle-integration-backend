from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.project import ProjectStatus, RiskLevel

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    symbol: str = Field(..., min_length=1, max_length=10, description="Token symbol")
    description: str = Field(..., min_length=10, description="Project description")
    category: str = Field(..., min_length=1, max_length=100, description="Project category")
    initial_supply: int = Field(..., gt=0, description="Initial token supply")
    end_date: datetime = Field(..., description="Project end date")
    risk_level: RiskLevel = Field(..., description="Project risk level")

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    image_url: Optional[str] = Field(None, max_length=500, description="Project image URL")
    business_plan_url: Optional[str] = Field(None, max_length=500, description="Business plan document URL")
    whitepaper_url: Optional[str] = Field(None, max_length=500, description="Whitepaper document URL")
    
    # IEO contract parameters
    delay_days: int = Field(default=7, ge=1, le=365, description="Claim and refund delay in days")
    min_investment: int = Field(default=100, ge=1, description="Minimum investment amount in USDC (6 decimals)")
    max_investment: int = Field(default=1000000, ge=1000, description="Maximum investment amount in USDC (6 decimals)")

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    initial_supply: Optional[int] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    risk_level: Optional[RiskLevel] = None
    image_url: Optional[str] = Field(None, max_length=500)
    business_plan_url: Optional[str] = Field(None, max_length=500)
    whitepaper_url: Optional[str] = Field(None, max_length=500)
    delay_days: Optional[int] = Field(None, ge=1, le=365)
    min_investment: Optional[int] = Field(None, ge=1)
    max_investment: Optional[int] = Field(None, ge=1000)

class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: str
    owner_id: str
    current_raised: Optional[Decimal] = None
    status: ProjectStatus
    image_url: Optional[str] = None
    business_plan_url: Optional[str] = None
    whitepaper_url: Optional[str] = None
    
    # IEO contract parameters
    delay_days: int
    min_investment: int
    max_investment: int
    
    # Updated blockchain details for 3 contracts
    token_contract_address: Optional[str] = None
    ieo_contract_address: Optional[str] = None
    reward_tracking_contract_address: Optional[str] = None
    
    # Deployment transaction hashes
    token_deployment_tx: Optional[str] = None
    ieo_deployment_tx: Optional[str] = None
    reward_tracking_deployment_tx: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectList(BaseModel):
    """Schema for project list response"""
    items: list[ProjectResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class ProjectStats(BaseModel):
    """Schema for project statistics"""
    total_projects: int
    active_projects: int
    total_raised: Decimal
    total_investors: int

class ProjectDeploymentResponse(BaseModel):
    """Schema for project deployment response - Updated for 3 contracts"""
    project_id: str
    token_contract_address: str
    ieo_contract_address: str
    reward_tracking_contract_address: str
    token_deployment_tx: str
    ieo_deployment_tx: str
    reward_tracking_deployment_tx: str
    deployment_status: str
