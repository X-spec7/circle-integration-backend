from sqlalchemy import Column, String, Text, DateTime, Enum, Numeric, BigInteger, ForeignKey, Integer
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
    initial_supply = Column(BigInteger, nullable=False)
    current_raised = Column(Numeric(15, 2), default=0)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    
    # IEO contract parameters
    delay_days = Column(Integer, default=7, nullable=False)
    min_investment = Column(Integer, default=100, nullable=False)  # USDC (6 decimals)
    max_investment = Column(Integer, default=1000000, nullable=False)  # USDC (6 decimals)
    
    # Business admin wallet
    business_admin_wallet = Column(String, nullable=True)  # Business admin wallet address
    
    # Blockchain contract addresses
    token_contract_address = Column(String, nullable=True)
    ieo_contract_address = Column(String, nullable=True)
    reward_tracking_contract_address = Column(String, nullable=True)
    
    # Deployment transaction hashes
    token_deployment_tx = Column(String, nullable=True)
    ieo_deployment_tx = Column(String, nullable=True)
    reward_tracking_deployment_tx = Column(String, nullable=True)

    # Sync cursor for blockchain events
    last_processed_block = Column(BigInteger, nullable=True)
    
    # Optional URLs
    image_url = Column(String(500), nullable=True)
    business_plan_url = Column(String(500), nullable=True)
    whitepaper_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    investments = relationship("Investment", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
