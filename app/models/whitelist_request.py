from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid

class WhitelistRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class WhitelistRequest(Base):
    __tablename__ = "whitelist_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    investor_id = Column(String, ForeignKey("users.id"), nullable=False)
    addresses = Column(Text, nullable=False)  # comma-separated addresses
    status = Column(Enum(WhitelistRequestStatus), default=WhitelistRequestStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WhitelistRequestAddress(Base):
    __tablename__ = "whitelist_request_addresses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("whitelist_requests.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    investor_id = Column(String, ForeignKey("users.id"), nullable=False)
    address = Column(String, nullable=False)
    status = Column(Enum(WhitelistRequestStatus), default=WhitelistRequestStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Full uniqueness as a fallback; actual partial unique applied via migration
        UniqueConstraint('project_id', 'address', name='uq_project_address'),
        Index('ix_whitelist_request_addresses_project', 'project_id'),
        Index('ix_whitelist_request_addresses_address', 'address'),
    ) 