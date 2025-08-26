from sqlalchemy import Column, String, DateTime, Enum, Numeric, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid

class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    CRYPTO = "crypto"
    FIAT = "fiat"

class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Investment(Base):
    """Investment model for tracking user investments"""
    __tablename__ = "investments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    tokens_received = Column(BigInteger, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String)  # Blockchain transaction hash
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    investor = relationship("User", back_populates="investments")
    project = relationship("Project", back_populates="investments")
    payment = relationship("Payment", back_populates="investment", uselist=False)

    def __repr__(self):
        return f"<Investment(id={self.id}, amount={self.amount}, status='{self.payment_status}')>" 