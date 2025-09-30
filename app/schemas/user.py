from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserType, UserStatus

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    user_type: UserType = Field(..., description="User type (SME, Investor, or Admin)")
    company: Optional[str] = Field(None, max_length=255, description="Company name (for SMEs)")

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserUpdate(BaseModel):
    """Schema for user updates"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    company: Optional[str] = Field(None, max_length=255)
    wallet_address: Optional[str] = Field(None, description="Wallet address for crypto payments")

class User(BaseModel):
    """Schema for user response"""
    id: str
    status: UserStatus
    is_active: bool
    kyc_verified: bool
    email: EmailStr
    username: str
    name: str
    user_type: UserType
    company: Optional[str] = None
    wallet_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: str
    email: str
    username: str
    name: str
    user_type: UserType
    company: Optional[str] = None
    status: UserStatus
    is_active: bool
    kyc_verified: bool
    wallet_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True 