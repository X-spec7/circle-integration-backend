from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.kyc import KycStatus


class KycClientCreate(BaseModel):
    client_type: str
    entity_name: str
    email: EmailStr


class KycClientOut(BaseModel):
    id: str
    complycube_client_id: str
    user_id: str
    client_type: str
    entity_name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: KycStatus
    status_text: Optional[str] = None

    class Config:
        from_attributes = True


class KycSessionCreate(BaseModel):
    session_type: Optional[str] = "document_check"
    redirect_url: str
    webhook_url: str


class KycSessionOut(BaseModel):
    id: str
    session_url: Optional[str] = None

