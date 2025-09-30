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
            # db.rollback()  # SQLAlchemy handles rollback automatically
    
    async def create_project(
        self,
        db: Session,
        user: User,
        project_data: ProjectCreate
    ) -> ProjectDeploymentResponse:
        """Create a new project with all 3 contracts deployment (Token, IEO, RewardTracking)"""
        try:
            # Validate user is SME
            if user.user_type != "sme":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only SMEs can create projects"
                )
            
            # Validate business admin wallet address
            if not project_data.business_admin_wallet:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Business admin wallet address is required"
                )
            
            # Basic wallet address validation (should start with 0x and be 42 characters)
            if not (project_data.business_admin_wallet.startswith('0x') and 
                    len(project_data.business_admin_wallet) == 42):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid business admin wallet address format"
                )
            
            logger.info(f"🚀 Starting project creation for: {project_data.name}")
            logger.info(f"👤 Owner: {user.name} ({user.email})")
            logger.info(f"🏢 Business admin wallet: {project_data.business_admin_wallet}")
            
            # STEP 1: Deploy contracts FIRST (before creating database record)
            logger.info(f"�� Step 1: Deploying smart contracts...")
            try:
                deployment_result = await blockchain_service.deploy_project_contracts({
                    "name": project_data.name,
                    "symbol": project_data.symbol,
                    "initial_supply": project_data.initial_supply,
                    "business_admin_wallet": project_data.business_admin_wallet,
                    "delay_days": project_data.delay_days,
                    "min_investment": project_data.min_investment,
                    "max_investment": project_data.max_investment
                })
                logger.info(f"✅ Smart contracts deployed successfully!")
            except Exception as e:
                logger.error(f"❌ Contract deployment failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Contract deployment failed: {str(e)}"
                )
            
            # STEP 2: Create project record in database (only after successful deployment)
            logger.info(f"📝 Step 2: Creating project record in database...")
            project = Project(
                owner_id=user.id,
                name=project_data.name,
                symbol=project_data.symbol,
                description=project_data.description,
                category=project_data.category,
                initial_supply=project_data.initial_supply,
                risk_level=project_data.risk_level,
                delay_days=project_data.delay_days,
                min_investment=project_data.min_investment,
                max_investment=project_data.max_investment,
                business_admin_wallet=project_data.business_admin_wallet,
                image_url=project_data.image_url,
                business_plan_url=project_data.business_plan_url,
                whitepaper_url=project_data.whitepaper_url,
                status=ProjectStatus.ACTIVE,  # Set to ACTIVE since contracts are deployed
                
                # Contract addresses from deployment
                token_contract_address=deployment_result["token_contract_address"],
                ieo_contract_address=deployment_result["ieo_contract_address"],
                reward_tracking_contract_address=deployment_result["reward_tracking_contract_address"],
                
                # Deployment transaction hashes
                token_deployment_tx=deployment_result["token_deployment_tx"],
                ieo_deployment_tx=deployment_result["ieo_deployment_tx"],
                reward_tracking_deployment_tx=deployment_result["reward_tracking_deployment_tx"]
            )
            
            db.add(project)
            db.commit()
            db.refresh(project)
            
            logger.info(f"✅ Project {project.id} created successfully in database!")
            logger.info(f"📍 Token contract: {deployment_result['token_contract_address']}")
            logger.info(f"📍 IEO contract: {deployment_result['ieo_contract_address']}")
            logger.info(f"📍 Reward tracking contract: {deployment_result['reward_tracking_contract_address']}")
            
            return ProjectDeploymentResponse(
                project_id=project.id,
                token_contract_address=deployment_result["token_contract_address"],
                ieo_contract_address=deployment_result["ieo_contract_address"],
                reward_tracking_contract_address=deployment_result["reward_tracking_contract_address"],
                token_deployment_tx=deployment_result["token_deployment_tx"],
                ieo_deployment_tx=deployment_result["ieo_deployment_tx"],
                reward_tracking_deployment_tx=deployment_result["reward_tracking_deployment_tx"],
                business_admin_wallet=project_data.business_admin_wallet,
                tokens_transferred=True,
                deployment_status="completed"
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error creating project: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create project: {str(e)}"
            )
    
    async def get_projects(
        self,
        db: Session,
        category: Optional[str] = None,
        risk_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Project]:
        """Get projects with optional filtering"""
        try:
            query = db.query(Project)

            query = query.filter(Project.status == "active")

            if category:
                query = query.filter(Project.category == category)
            if risk_level:
                query = query.filter(Project.risk_level == risk_level)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get projects"
            )
    
    async def get_project_by_id(self, db: Session, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        try:
            return db.query(Project).filter(Project.id == project_id).first()
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get project"
            )
    
    async def update_project(
        self,
        db: Session,
        project_id: str,
        project_data: dict,
        user: User
    ) -> Project:
        """Update project (only by owner)"""
        try:
            project = await self.get_project_by_id(db, project_id)
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
            for field, value in project_data.items():
                if hasattr(project, field) and value is not None:
                    setattr(project, field, value)
            
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            
            return project
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project"
            )
    
    async def delete_project(
        self,
        db: Session,
        project_id: str,
        user: User
    ) -> bool:
        """Delete project (only by owner)"""
        try:
            project = await self.get_project_by_id(db, project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if project.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only project owner can delete project"
                )
            
            db.delete(project)
            db.commit()
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )

# Create service instance
project_service = ProjectService()
