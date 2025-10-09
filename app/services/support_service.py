from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from fastapi import HTTPException, status

from app.models.support import (
    TicketCategory,
    SupportTicket,
    TicketParticipant,
    TicketMessage,
    TicketStatus,
)
from app.models.user import User, UserType
from app.schemas.support import (
    TicketCategoryCreate,
    TicketCategoryUpdate,
    SupportTicketCreate,
    TicketMessageCreate,
)


class SupportService:
    """Service layer for support tickets, categories, participants, and messages"""

    # Categories
    @staticmethod
    def create_category(db: Session, data: TicketCategoryCreate) -> TicketCategory:
        exists = db.query(TicketCategory).filter(TicketCategory.name == data.name).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
        category = TicketCategory(name=data.name, description=data.description, is_active=data.is_active)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def list_categories(db: Session, active_only: bool = True) -> List[TicketCategory]:
        q = db.query(TicketCategory)
        if active_only:
            q = q.filter(TicketCategory.is_active == True)  # noqa: E712
        return q.order_by(TicketCategory.name.asc()).all()

    @staticmethod
    def update_category(db: Session, category_id: str, data: TicketCategoryUpdate) -> TicketCategory:
        category = db.query(TicketCategory).filter(TicketCategory.id == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data:
            existing = (
                db.query(TicketCategory)
                .filter(and_(TicketCategory.name == update_data["name"], TicketCategory.id != category_id))
                .first()
            )
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
        for field, value in update_data.items():
            setattr(category, field, value)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: str) -> None:
        category = db.query(TicketCategory).filter(TicketCategory.id == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        db.delete(category)
        db.commit()

    # Tickets
    @staticmethod
    def _assert_no_open_ticket_in_category(db: Session, creator_id: str, category_id: str) -> None:
        open_ticket = (
            db.query(SupportTicket)
            .filter(
                SupportTicket.creator_id == creator_id,
                SupportTicket.category_id == category_id,
                SupportTicket.status == TicketStatus.OPEN,
            )
            .first()
        )
        if open_ticket:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An open ticket already exists for this category",
            )

    @staticmethod
    def create_ticket(db: Session, creator: User, data: SupportTicketCreate) -> SupportTicket:
        category = db.query(TicketCategory).filter(TicketCategory.id == data.category_id, TicketCategory.is_active == True).first()  # noqa: E712
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")
        SupportService._assert_no_open_ticket_in_category(db, creator.id, data.category_id)
        ticket = SupportTicket(title=data.title, creator_id=creator.id, category_id=data.category_id)
        db.add(ticket)
        db.flush()
        # creator is implicit participant
        participant = TicketParticipant(ticket_id=ticket.id, user_id=creator.id, is_admin_invited=False)
        db.add(participant)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def close_ticket(db: Session, ticket_id: str, requester: User) -> SupportTicket:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        if requester.user_type != UserType.ADMIN and ticket.creator_id != requester.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to close this ticket")
        ticket.status = TicketStatus.CLOSED
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: str, user: User) -> SupportTicket:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        # Allow creator, any participant, or admin
        if user.user_type != UserType.ADMIN:
            is_participant = (
                db.query(TicketParticipant)
                .filter(TicketParticipant.ticket_id == ticket_id, TicketParticipant.user_id == user.id)
                .first()
                is not None
            )
            if not is_participant and ticket.creator_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        return ticket

    @staticmethod
    def list_user_tickets(db: Session, user: User, category_id: Optional[str] = None) -> List[SupportTicket]:
        q = db.query(SupportTicket)
        if user.user_type == UserType.ADMIN:
            if category_id:
                q = q.filter(SupportTicket.category_id == category_id)
            tickets = q.order_by(SupportTicket.created_at.desc()).all()
            # No unread concept for admin globally; compute per admin if needed (skip for now)
            return tickets
        # non-admin: tickets they created or participate in
        ticket_ids = [tp.ticket_id for tp in db.query(TicketParticipant).filter(TicketParticipant.user_id == user.id).all()]
        q = q.filter(
            (SupportTicket.creator_id == user.id) | (SupportTicket.id.in_(ticket_ids))
        )
        if category_id:
            q = q.filter(SupportTicket.category_id == category_id)
        tickets = q.order_by(SupportTicket.created_at.desc()).all()
        # annotate unread_count and last_unread_message
        for t in tickets:
            # participant row holds last_read_at
            participant = (
                db.query(TicketParticipant)
                .filter(TicketParticipant.ticket_id == t.id, TicketParticipant.user_id == user.id)
                .first()
            )
            last_read_at = participant.last_read_at if participant else None
            unread_q = db.query(TicketMessage).filter(TicketMessage.ticket_id == t.id)
            if last_read_at is not None:
                unread_q = unread_q.filter(TicketMessage.created_at > last_read_at)
            unread_count = unread_q.count()
            setattr(t, "unread_count", unread_count)
            last_unread = unread_q.order_by(TicketMessage.created_at.desc()).first()
            if last_unread:
                setattr(t, "last_unread_message", last_unread)
            else:
                setattr(t, "last_unread_message", None)
        return tickets

    # Participants
    @staticmethod
    def invite_participant(db: Session, ticket_id: str, target_user_id: str, inviter: User) -> TicketParticipant:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        # Only admin can invite; optionally allow creator too if desired; spec says admin can invite
        if inviter.user_type != UserType.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can invite participants")
        existing = (
            db.query(TicketParticipant)
            .filter(TicketParticipant.ticket_id == ticket_id, TicketParticipant.user_id == target_user_id)
            .first()
        )
        if existing:
            return existing
        participant = TicketParticipant(ticket_id=ticket_id, user_id=target_user_id, is_admin_invited=True)
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    # Messages
    @staticmethod
    def _ensure_can_participate(db: Session, ticket_id: str, user: User) -> None:
        if user.user_type == UserType.ADMIN:
            return
        is_participant = (
            db.query(TicketParticipant)
            .filter(TicketParticipant.ticket_id == ticket_id, TicketParticipant.user_id == user.id)
            .first()
            is not None
        )
        if not is_participant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant of this ticket")

    @staticmethod
    def add_message(db: Session, ticket_id: str, sender: User, data: TicketMessageCreate) -> TicketMessage:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        if ticket.status != TicketStatus.OPEN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add message to a closed ticket")
        SupportService._ensure_can_participate(db, ticket_id, sender)
        msg = TicketMessage(ticket_id=ticket_id, sender_id=sender.id, content=data.content)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def list_messages(db: Session, ticket_id: str, user: User, page: int = 1, limit: int = 50) -> Tuple[List[TicketMessage], int]:
        SupportService._ensure_can_participate(db, ticket_id, user)
        q = db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at.asc())
        total = q.count()
        items = q.offset((page - 1) * limit).limit(limit).all()
        return items, total

    @staticmethod
    def mark_as_read(db: Session, ticket_id: str, user: User) -> None:
        SupportService._ensure_can_participate(db, ticket_id, user)
        participant = (
            db.query(TicketParticipant)
            .filter(TicketParticipant.ticket_id == ticket_id, TicketParticipant.user_id == user.id)
            .first()
        )
        if not participant:
            # creator may not have an explicit participant row (but we create it at ticket creation); handle gracefully
            participant = TicketParticipant(ticket_id=ticket_id, user_id=user.id, is_admin_invited=False)
            db.add(participant)
        participant.last_read_at = func.now()
        db.commit()


support_service = SupportService()

