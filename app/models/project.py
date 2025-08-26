from sqlalchemy import Column, String, Text, DateTime, Enum, Numeric, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid

class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"

class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Project(Base):
    """Project model for token projects"""
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String(10), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    price_per_token = Column(Numeric(10, 4), nullable=False)
    total_supply = Column(BigInteger, nullable=False)
    current_raised = Column(Numeric(15, 2), default=0)
    end_date = Column(DateTime, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    
    # File URLs
    image_url = Column(String(500))
    business_plan_url = Column(String(500))
    whitepaper_url = Column(String(500))
    
    # Blockchain details
    token_contract_address = Column(String)  # Polygon token contract
    escrow_contract_address = Column(String)  # Escrow smart contract
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    investments = relationship("Investment", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>" 