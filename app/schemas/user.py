from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserType

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    user_type: UserType = Field(..., description="User type (SME or Investor)")

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
    user_type: Optional[UserType] = None
    is_active: Optional[bool] = None

class User(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: int
    email: str
    username: str
    user_type: UserType
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True 