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
    initial_supply = Column(BigInteger, nullable=False)  # Changed from total_supply
    current_raised = Column(Numeric(15, 2), default=0)
    end_date = Column(DateTime, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    
    # IEO contract parameters
    delay_days = Column(Integer, default=7, nullable=False)
    min_investment = Column(Integer, default=100, nullable=False)  # USDC (6 decimals)
    max_investment = Column(Integer, default=1000000, nullable=False)  # USDC (6 decimals)
    
    # File URLs
    image_url = Column(String(500))
    business_plan_url = Column(String(500))
    whitepaper_url = Column(String(500))
    
    # Blockchain details - Updated for 3 contracts
    token_contract_address = Column(String)  # FundraisingToken contract
    ieo_contract_address = Column(String)    # IEO contract
    reward_tracking_contract_address = Column(String)  # RewardTracking contract
    
    # Deployment transaction hashes
    token_deployment_tx = Column(String)  # Token deployment transaction hash
    ieo_deployment_tx = Column(String)    # IEO deployment transaction hash
    reward_tracking_deployment_tx = Column(String)  # RewardTracking deployment transaction hash
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    investments = relationship("Investment", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
