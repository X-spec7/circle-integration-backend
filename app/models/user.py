from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid

class UserType(str, enum.Enum):
    """User type enumeration"""
    SME = "sme"
    INVESTOR = "investor"
    ADMIN = "admin"

class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    """Enhanced User model with additional fields"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.INVESTOR)
    company = Column(String)  # For SMEs
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    kyc_verified = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    wallet_address = Column(String)  # For crypto payments
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="owner")
    investments = relationship("Investment", back_populates="investor")
    sessions = relationship("UserSession", back_populates="user")
    kyc_clients = relationship("KycClient", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', type='{self.user_type}')>" 