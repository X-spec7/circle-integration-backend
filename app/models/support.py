from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class TicketCategory(Base):
    __tablename__ = "ticket_categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tickets = relationship("SupportTicket", back_populates="category")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(String, ForeignKey("ticket_categories.id"), nullable=False, index=True)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("TicketCategory", back_populates="tickets")
    participants = relationship("TicketParticipant", back_populates="ticket", cascade="all, delete-orphan")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_unique_open_ticket_per_category_creator", "creator_id", "category_id", unique=False),
    )


class TicketParticipant(Base):
    __tablename__ = "ticket_participants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, ForeignKey("support_tickets.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    is_admin_invited = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_read_at = Column(DateTime(timezone=True), nullable=True)

    ticket = relationship("SupportTicket", back_populates="participants")

    __table_args__ = (
        Index("ux_ticket_participant", "ticket_id", "user_id", unique=True),
    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, ForeignKey("support_tickets.id"), nullable=False, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("SupportTicket", back_populates="messages")


