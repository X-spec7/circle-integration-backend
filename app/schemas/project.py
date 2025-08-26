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
    target_amount: Decimal = Field(..., gt=0, description="Target fundraising amount")
    price_per_token: Decimal = Field(..., gt=0, description="Price per token")
    total_supply: int = Field(..., gt=0, description="Total token supply")
    end_date: datetime = Field(..., description="Project end date")
    risk_level: RiskLevel = Field(..., description="Project risk level")

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    image_url: Optional[str] = Field(None, max_length=500, description="Project image URL")
    business_plan_url: Optional[str] = Field(None, max_length=500, description="Business plan document URL")
    whitepaper_url: Optional[str] = Field(None, max_length=500, description="Whitepaper document URL")

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    target_amount: Optional[Decimal] = Field(None, gt=0)
    price_per_token: Optional[Decimal] = Field(None, gt=0)
    total_supply: Optional[int] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    risk_level: Optional[RiskLevel] = None
    image_url: Optional[str] = Field(None, max_length=500)
    business_plan_url: Optional[str] = Field(None, max_length=500)
    whitepaper_url: Optional[str] = Field(None, max_length=500)

class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: str
    owner_id: str
    current_raised: Optional[Decimal] = None
    status: ProjectStatus
    image_url: Optional[str] = None
    business_plan_url: Optional[str] = None
    whitepaper_url: Optional[str] = None
    token_contract_address: Optional[str] = None
    escrow_contract_address: Optional[str] = None
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