from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserType(str, enum.Enum):
    """User type enumeration"""
    SME = "sme"
    INVESTOR = "investor"

class User(Base):
    """User model with type support"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.SME)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (for future features)
    # profile = relationship("UserProfile", back_populates="user", uselist=False)
    # investments = relationship("Investment", back_populates="investor")
    # projects = relationship("Project", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', type='{self.user_type}')>" 