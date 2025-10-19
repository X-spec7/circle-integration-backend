from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid


class DocumentSigningStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DocumentSigning(Base):
    __tablename__ = "document_signings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    envelope_id = Column(String, unique=True, nullable=False)
    document_name = Column(String, nullable=False)
    document_path = Column(String, nullable=True)
    document_type = Column(String, nullable=False)
    status = Column(Enum(DocumentSigningStatus), default=DocumentSigningStatus.DRAFT)
    signing_service = Column(String(50), nullable=False)

    # Associations (all optional except user)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    investment_id = Column(String, ForeignKey("investments.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    signed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")
    project = relationship("Project")
    investment = relationship("Investment")
    signers = relationship("DocumentSigner", back_populates="document_signing", cascade="all, delete-orphan")


class DocumentSigner(Base):
    __tablename__ = "document_signers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_signing_id = Column(String, ForeignKey("document_signings.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="signer")
    signer_order = Column(Integer, default=1)
    signed_at = Column(DateTime(timezone=True), nullable=True)

    document_signing = relationship("DocumentSigning", back_populates="signers")


