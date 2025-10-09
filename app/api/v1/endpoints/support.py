from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.schemas.support import (
    TicketCategoryCreate,
    TicketCategoryUpdate,
    TicketCategoryOut,
    SupportTicketCreate,
    SupportTicketOut,
    TicketMessageCreate,
    TicketMessageOut,
    TicketParticipantInvite,
    TicketParticipantOut,
    PaginatedMessages,
)
from app.services.support_service import support_service


router = APIRouter()


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# Categories (Admin only for write)
@router.post("/categories", response_model=TicketCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: TicketCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return support_service.create_category(db, data)


@router.get("/categories", response_model=List[TicketCategoryOut])
def list_categories(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return support_service.list_categories(db, active_only)


@router.put("/categories/{category_id}", response_model=TicketCategoryOut)
def update_category(
    category_id: str,
    data: TicketCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return support_service.update_category(db, category_id, data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    support_service.delete_category(db, category_id)


# Tickets
@router.post("/tickets", response_model=SupportTicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return support_service.create_ticket(db, current_user, data)


@router.get("/tickets", response_model=List[SupportTicketOut])
def list_tickets(
    category_id: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return support_service.list_user_tickets(db, current_user, category_id)


@router.get("/tickets/{ticket_id}", response_model=SupportTicketOut)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return support_service.get_ticket(db, ticket_id, current_user)


@router.post("/tickets/{ticket_id}/close", response_model=SupportTicketOut)
def close_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return support_service.close_ticket(db, ticket_id, current_user)


@router.post("/tickets/{ticket_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_ticket_read(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    support_service.mark_as_read(db, ticket_id, current_user)


# Participants (admin invite)
@router.post("/tickets/{ticket_id}/participants", response_model=TicketParticipantOut, status_code=status.HTTP_201_CREATED)
def invite_participant(
    ticket_id: str,
    invite: TicketParticipantInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return support_service.invite_participant(db, ticket_id, invite.user_id, current_user)


# Messages
@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageOut, status_code=status.HTTP_201_CREATED)
def create_message(
    ticket_id: str,
    data: TicketMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return support_service.add_message(db, ticket_id, current_user, data)


@router.get("/tickets/{ticket_id}/messages", response_model=PaginatedMessages)
def list_messages(
    ticket_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = support_service.list_messages(db, ticket_id, current_user, page, limit)
    total_pages = (total + limit - 1) // limit
    return {"items": items, "total": total, "page": page, "limit": limit, "total_pages": total_pages}


