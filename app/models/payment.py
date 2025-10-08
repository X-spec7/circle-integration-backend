from sqlalchemy import Column, String, DateTime, Enum, Numeric, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid

class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Payment(Base):
    """Payment model for tracking payment details"""
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    investment_id = Column(String, ForeignKey("investments.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), nullable=False)  # EUR, USDC, etc.
    payment_method = Column(String(20), nullable=False)  # crypto, fiat
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Circle integration
    circle_payment_id = Column(String)
    circle_transfer_id = Column(String)
    crypto_payout_succeeded = Column(Boolean, default=False)
    investment_recorded = Column(Boolean, default=False)
    
    # Blockchain details
    investor_wallet_address = Column(String)  # investor wallet to receive refunds/claims
    transaction_hash = Column(String)  # Blockchain transaction hash
    ieo_transaction_hash = Column(String)  # Transfer to IEO transaction
    blockchain_tx_hash = Column(String)  # EUR/USDC conversion tx or reference
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    investment = relationship("Investment", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status='{self.status}')>" 