"""
Project Service for managing projects and their blockchain deployments
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectDeploymentResponse
from app.services.blockchain_service import blockchain_service

logger = logging.getLogger(__name__)

class ProjectService:
    """Service for project operations including blockchain deployments"""
    
    async def cleanup_failed_deployment(self, project_id: str, db: Session):
        """Clean up a project if deployment fails"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.REJECTED
                db.commit()
                logger.info(f"Project {project_id} marked as rejected due to deployment failure")
        except Exception as e:
            logger.error(f"Error cleaning up failed project {project_id}: {str(e)}")
            db.rollback()
    
    async def create_project(
        self,
        db: Session,
        user: User,
        project_data: ProjectCreate
    ) -> ProjectDeploymentResponse:
        """Create a new project with all 3 contracts deployment (Token, IEO, RewardTracking)"""
        # Start a database transaction
        db.begin()
        
        try:
            # Validate user is SME
            if user.user_type != "sme":
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only SMEs can create projects"
                )
            
            # Create project record with PENDING status
            project = Project(
                owner_id=user.id,
                name=project_data.name,
                symbol=project_data.symbol,
                description=project_data.description,
                category=project_data.category,
                initial_supply=project_data.initial_supply,
                end_date=project_data.end_date,
                risk_level=project_data.risk_level,
                delay_days=project_data.delay_days,
                min_investment=project_data.min_investment,
                max_investment=project_data.max_investment,
                image_url=project_data.image_url,
                business_plan_url=project_data.business_plan_url,
                whitepaper_url=project_data.whitepaper_url,
                status=ProjectStatus.PENDING
            )
            
            db.add(project)
            db.flush()  # Get the ID without committing
            db.refresh(project)
            
            # Deploy all 3 contracts
            logger.info(f"Deploying contracts for project {project.id}")
            try:
                deployment_result = await blockchain_service.deploy_project_contracts(
                    name=project_data.name,
                    symbol=project_data.symbol,
                    initial_supply=project_data.initial_supply,
                    admin_address=blockchain_service.account.address,
                    business_admin_address=blockchain_service.account.address,
                    delay_days=project_data.delay_days,
                    min_investment=project_data.min_investment,
                    max_investment=project_data.max_investment
                )
            except Exception as e:
                logger.error(f"Contract deployment failed for project {project.id}: {str(e)}")
                await self.cleanup_failed_deployment(project.id, db)
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Contract deployment failed: {str(e)}"
                )
            
            # Update project with all contract addresses and set status to ACTIVE
            project.token_contract_address = deployment_result['token_contract']['address']
            project.ieo_contract_address = deployment_result['ieo_contract']['address']
            project.reward_tracking_contract_address = deployment_result['reward_tracking_contract']['address']
            
            project.token_deployment_tx = deployment_result['token_contract']['deployment']['transaction_hash']
            project.ieo_deployment_tx = deployment_result['ieo_contract']['deployment']['transaction_hash']
            project.reward_tracking_deployment_tx = deployment_result['reward_tracking_contract']['deployment']['transaction_hash']
            
            project.status = ProjectStatus.ACTIVE
            
            # Commit the transaction only if everything succeeded
            db.commit()
            
            logger.info(f"Project {project.id} created successfully with all contracts deployed")
            
            return ProjectDeploymentResponse(
                project_id=project.id,
                token_contract_address=deployment_result['token_contract']['address'],
                ieo_contract_address=deployment_result['ieo_contract']['address'],
                reward_tracking_contract_address=deployment_result['reward_tracking_contract']['address'],
                token_deployment_tx=deployment_result['token_contract']['deployment']['transaction_hash'],
                ieo_deployment_tx=deployment_result['ieo_contract']['deployment']['transaction_hash'],
                reward_tracking_deployment_tx=deployment_result['reward_tracking_contract']['deployment']['transaction_hash'],
                deployment_status="completed"
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions without additional rollback
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating project: {str(e)}")
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
        status: Optional[str] = None,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Project]:
        """Get projects with optional filters"""
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == status)
        if category:
            query = query.filter(Project.category == category)
        if risk_level:
            query = query.filter(Project.risk_level == risk_level)
        
        return query.offset(skip).limit(limit).all()
    
    async def update_project(
        self,
        db: Session,
        project_id: str,
        user: User,
        update_data: dict
    ) -> Optional[Project]:
        """Update project (only by owner)"""
        project = await self.get_project(db, project_id)
        
        if not project:
            return None
        
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update project"
            )
        
        # Update allowed fields
        for field, value in update_data.items():
            if hasattr(project, field) and field not in ['id', 'owner_id', 'created_at']:
                setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
        
        return project
    
    async def delete_project(
        self,
        db: Session,
        project_id: str,
        user: User
    ) -> bool:
        """Delete project (only by owner)"""
        project = await self.get_project(db, project_id)
        
        if not project:
            return False
        
        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can delete project"
            )
        
        db.delete(project)
        db.commit()
        
        return True

# Global instance
project_service = ProjectService()
