from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid


class KycStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    REVIEW = "review"
    VERIFIED = "verified"
    DECLINED = "declined"


class KycClient(Base):
    __tablename__ = "kyc_clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    complycube_client_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    client_type = Column(String, nullable=False)  # 'person' or 'company'
    entity_name = Column(String)
    email = Column(String)
    status = Column(Enum(KycStatus), default=KycStatus.NOT_STARTED)
    status_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    personal_details = relationship("KycPersonalDetails", back_populates="kyc_client", uselist=False)
    company_details = relationship("KycCompanyDetails", back_populates="kyc_client", uselist=False)
    documents = relationship("KycDocument", back_populates="kyc_client")
    user = relationship("User", back_populates="kyc_clients")


class KycPersonalDetails(Base):
    __tablename__ = "kyc_personal_details"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kyc_client_id = Column(String, ForeignKey("kyc_clients.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    date_of_birth = Column(String)
    nationality = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    kyc_client = relationship("KycClient", back_populates="personal_details")


class KycCompanyDetails(Base):
    __tablename__ = "kyc_company_details"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kyc_client_id = Column(String, ForeignKey("kyc_clients.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_name = Column(String)
    registration_number = Column(String)
    incorporation_date = Column(String)
    business_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    kyc_client = relationship("KycClient", back_populates="company_details")


class KycDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kyc_client_id = Column(String, ForeignKey("kyc_clients.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_type = Column(String)
    document_number = Column(String)
    complycube_document_id = Column(String)  # ComplyCube document ID
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    kyc_client = relationship("KycClient", back_populates="documents")


