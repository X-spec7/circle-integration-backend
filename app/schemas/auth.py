from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in minutes")

class TokenData(BaseModel):
    """Schema for token payload data"""
    email: Optional[str] = None
    user_type: Optional[str] = None

class AuthResponse(BaseModel):
    """Schema for authentication response"""
    user: dict
    token: Token 