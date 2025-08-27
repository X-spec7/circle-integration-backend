"""
Project Service for managing projects and blockchain deployments
"""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectDeploymentResponse
from app.services.blockchain_service import blockchain_service

logger = logging.getLogger(__name__)

class ProjectService:
    """Service for project operations including blockchain deployments"""
    
    async def create_project(
        self,
        db: Session,
        user: User,
        project_data: ProjectCreate
    ) -> ProjectDeploymentResponse:
        """Create a new project with ERC20 token and escrow contract deployment"""
        try:
            # Validate user is SME
            if user.user_type != "sme":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only SMEs can create projects"
                )
            
            # Create project record
            project = Project(
                owner_id=user.id,
                name=project_data.name,
                symbol=project_data.symbol,
                description=project_data.description,
                category=project_data.category,
                target_amount=project_data.target_amount,
                price_per_token=project_data.price_per_token,
                total_supply=project_data.total_supply,
                end_date=project_data.end_date,
                risk_level=project_data.risk_level,
                image_url=project_data.image_url,
                business_plan_url=project_data.business_plan_url,
                whitepaper_url=project_data.whitepaper_url,
                status=ProjectStatus.PENDING
            )
            
            db.add(project)
            db.commit()
            db.refresh(project)
            
            # Deploy ERC20 token contract
            logger.info(f"Deploying ERC20 token for project {project.id}")
            token_address, token_deployment = await blockchain_service.deploy_erc20_token(
                name=project_data.name,
                symbol=project_data.symbol,
                total_supply=project_data.total_supply,
                price_per_token=project_data.price_per_token,
                owner_address=user.wallet_address or self.account.address
            )
            
            # Deploy escrow contract
            logger.info(f"Deploying escrow contract for project {project.id}")
            escrow_address, escrow_deployment = await blockchain_service.deploy_escrow_contract(
                project_token_address=token_address,
                project_owner_address=user.wallet_address or self.account.address,
                target_amount=project_data.target_amount,
                token_price=project_data.price_per_token,
                end_date=int(project_data.end_date.timestamp())
            )
            
            # Update project with contract addresses
            project.token_contract_address = token_address
            project.escrow_contract_address = escrow_address
            project.token_deployment_tx = token_deployment["transaction_hash"]
            project.escrow_deployment_tx = escrow_deployment["transaction_hash"]
            project.status = ProjectStatus.ACTIVE
            
            db.commit()
            db.refresh(project)
            
            logger.info(f"Project {project.id} created successfully with contracts deployed")
            
            return ProjectDeploymentResponse(
                project_id=project.id,
                token_contract_address=token_address,
                escrow_contract_address=escrow_address,
                token_deployment_tx=token_deployment["transaction_hash"],
                escrow_deployment_tx=escrow_deployment["transaction_hash"],
                deployment_status="completed"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create project: {str(e)}"
            )
    
    async def get_project(self, db: Session, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return db.query(Project).filter(Project.id == project_id).first()
    
    async def get_projects(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatus] = None
    ):
        """Get projects with optional filtering"""
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    async def update_project(
        self,
        db: Session,
        project_id: str,
        user: User,
        update_data: Dict[str, Any]
    ) -> Project:
        """Update project (owner only)"""
        project = await self.get_project(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update project"
            )
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(project, field) and value is not None:
                setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        
        return project
    
    async def get_project_stats(self, db: Session) -> Dict[str, Any]:
        """Get project statistics"""
        total_projects = db.query(Project).count()
        active_projects = db.query(Project).filter(Project.status == ProjectStatus.ACTIVE).count()
        
        # Calculate total raised
        total_raised = db.query(Project.current_raised).filter(
            Project.status == ProjectStatus.ACTIVE
        ).all()
        total_raised_sum = sum([p[0] or 0 for p in total_raised])
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_raised": total_raised_sum
        }
    
    async def get_escrow_address(self, db: Session, project_id: str) -> Optional[str]:
        """Get escrow address for a project"""
        project = await self.get_project(db, project_id)
        return project.escrow_contract_address if project else None

# Global project service instance
project_service = ProjectService() 