from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import UserType


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    user_ids: Optional[List[str]] = None
    user_type: Optional[UserType] = None  # target SME or INVESTOR if user_ids not provided


class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    created_at: datetime
    read: bool
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationSettingsUpdate(BaseModel):
    notifications_enabled: bool


class NotificationSettingsOut(BaseModel):
    notifications_enabled: bool

