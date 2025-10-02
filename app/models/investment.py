from sqlalchemy import Column, String, Text, DateTime, Enum, Numeric, BigInteger, ForeignKey, Boolean, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid

class InvestmentStatus(str, enum.Enum):
    """Investment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CLAIMED = "claimed"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    CRYPTO = "crypto"
    FIAT = "fiat"

class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Investment(Base):
    """Investment model for tracking user investments"""
    __tablename__ = "investments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    investor_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Investment details
    usdc_amount = Column(Numeric(15, 6), nullable=False)  # USDC amount (6 decimals)
    token_amount = Column(Numeric(20, 18), nullable=False)  # Token amount (18 decimals)
    investment_time = Column(DateTime, nullable=False)
    investor_wallet_address = Column(String, nullable=True)
    
    # Status tracking
    status = Column(Enum(InvestmentStatus), default=InvestmentStatus.PENDING)
    claimed = Column(Boolean, default=False)
    refunded = Column(Boolean, default=False)
    
    # Blockchain details
    transaction_hash = Column(String, nullable=True)
    block_number = Column(BigInteger, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    investor = relationship("User", back_populates="investments")
    project = relationship("Project", back_populates="investments")
    payment = relationship("Payment", back_populates="investment", uselist=False)

    def __repr__(self):
        return f"<Investment(id={self.id}, investor_id={self.investor_id}, project_id={self.project_id}, amount={self.usdc_amount})>"
