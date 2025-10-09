from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.support import TicketStatus


class TicketCategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = True


class TicketCategoryCreate(TicketCategoryBase):
    pass


class TicketCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None


class TicketCategoryOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SupportTicketCreate(BaseModel):
    category_id: str
    title: str = Field(..., min_length=2, max_length=200)


class SupportTicketOut(BaseModel):
    id: str
    title: str
    category_id: str
    creator_id: str
    status: TicketStatus
    created_at: datetime
    # UX additions
    unread_count: int | None = None
    last_unread_message: 'TicketMessageOut' | None = None

    class Config:
        from_attributes = True


class TicketMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class TicketMessageOut(BaseModel):
    id: str
    ticket_id: str
    sender_id: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketParticipantInvite(BaseModel):
    user_id: str


class TicketParticipantOut(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    is_admin_invited: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedMessages(BaseModel):
    items: List[TicketMessageOut]
    total: int
    page: int
    limit: int
    total_pages: int

SupportTicketOut.model_rebuild()


