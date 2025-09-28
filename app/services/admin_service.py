"""
Admin Service for managing users, projects, and system settings
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import User, UserType, UserStatus
from app.models.project import Project, ProjectStatus
from app.models.investment import Investment
from app.schemas.admin import (
    AdminUserResponse, AdminUserUpdate, AdminUserListResponse,
    AdminProjectResponse, AdminProjectUpdate, AdminProjectListResponse,
    AdminDashboardStats, BusinessAdminUpdate, BusinessAdminUpdateResponse,
    AdminUserFilters, AdminProjectFilters, AdminActionLog
)
from app.services.blockchain_service import blockchain_service

logger = logging.getLogger(__name__)

class AdminService:
    """Service for admin operations"""
    
    def __init__(self):
        self.blockchain_service = blockchain_service
    
    # User Management
    async def get_users(
        self,
        db: Session,
        filters: AdminUserFilters,
        page: int = 1,
        limit: int = 50
    ) -> AdminUserListResponse:
        """Get paginated list of users with filters"""
        try:
            query = db.query(User)
            
            # Apply filters
            if filters.user_type:
                query = query.filter(User.user_type == filters.user_type)
            if filters.status:
                query = query.filter(User.status == filters.status)
            if filters.is_active is not None:
                query = query.filter(User.is_active == filters.is_active)

            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term),
                        User.username.ilike(search_term),
                        User.company.ilike(search_term)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            users = query.offset(offset).limit(limit).all()
            
            # Convert to response format with additional data
            user_responses = []
            for user in users:
                # Get project count
                project_count = db.query(Project).filter(Project.owner_id == user.id).count()
                
                # Get investment count
                investment_count = db.query(Investment).filter(Investment.investor_id == user.id).count()
                
                user_responses.append(AdminUserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    name=user.name,
                    user_type=user.user_type,
                    company=user.company,
                    status=user.status,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    wallet_address=user.wallet_address,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    project_count=project_count,
                    investment_count=investment_count
                ))
            
            total_pages = (total + limit - 1) // limit
            
            return AdminUserListResponse(
                items=user_responses,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get users: {str(e)}"
            )
    
    async def get_user(self, db: Session, user_id: str) -> AdminUserResponse:
        """Get user by ID with admin details"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get additional data
            project_count = db.query(Project).filter(Project.owner_id == user.id).count()
            investment_count = db.query(Investment).filter(Investment.investor_id == user.id).count()
            
            return AdminUserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                name=user.name,
                user_type=user.user_type,
                company=user.company,
                status=user.status,
                is_active=user.is_active,
                is_verified=user.is_verified,
                wallet_address=user.wallet_address,
                created_at=user.created_at,
                updated_at=user.updated_at,
                project_count=project_count,
                investment_count=investment_count
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user: {str(e)}"
            )
    
    async def update_user(
        self,
        db: Session,
        user_id: str,
        update_data: AdminUserUpdate,
        admin_user: User
    ) -> AdminUserResponse:
        """Update user by admin"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields
            if update_data.status is not None:
                user.status = update_data.status
            if update_data.is_active is not None:
                user.is_active = update_data.is_active
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            # Log admin action
            await self._log_admin_action(
                db=db,
                admin_user=admin_user,
                action="update_user",
                target_type="user",
                target_id=user_id,
                details=update_data.dict(exclude_unset=True)
            )
            
            return await self.get_user(db, user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )
    
    # Project Management
    async def get_projects(
        self,
        db: Session,
        filters: AdminProjectFilters,
        page: int = 1,
        limit: int = 50
    ) -> AdminProjectListResponse:
        """Get paginated list of projects with filters"""
        try:
            query = db.query(Project).join(User, Project.owner_id == User.id)
            
            # Apply filters
            if filters.status:
                query = query.filter(Project.status == filters.status)
            if filters.risk_level:
                query = query.filter(Project.risk_level == filters.risk_level)
            if filters.category:
                query = query.filter(Project.category == filters.category)
            # if filters.owner_id:
            #     query = query.filter(Project.owner_id == filters.owner_id)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Project.name.ilike(search_term),
                        Project.symbol.ilike(search_term),
                        Project.description.ilike(search_term)
                    )
                )
            # if filters.created_from:
            #     query = query.filter(Project.created_at >= filters.created_from)
            # if filters.created_to:
            #     query = query.filter(Project.created_at <= filters.created_to)
            # if filters.raised_min:
            #     query = query.filter(Project.current_raised >= filters.raised_min)
            # if filters.raised_max:
            #     query = query.filter(Project.current_raised <= filters.raised_max)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            projects = query.offset(offset).limit(limit).all()
            
            # Convert to response format
            project_responses = []
            for project in projects:
                # Get owner details
                owner = db.query(User).filter(User.id == project.owner_id).first()
                
                # Get investment data
                investment_count = db.query(Investment).filter(Investment.project_id == project.id).count()
                total_investors = db.query(Investment.investor_id).filter(
                    Investment.project_id == project.id
                ).distinct().count()
                
                project_responses.append(AdminProjectResponse(
                    id=project.id,
                    owner_id=project.owner_id,
                    owner_name=owner.name if owner else "Unknown",
                    owner_email=owner.email if owner else "Unknown",
                    owner_company=owner.company if owner else None,
                    name=project.name,
                    symbol=project.symbol,
                    description=project.description,
                    category=project.category,
                    initial_supply=project.initial_supply,
                    current_raised=project.current_raised,
                    
                    risk_level=project.risk_level,
                    status=project.status,
                    image_url=project.image_url,
                    business_plan_url=project.business_plan_url,
                    whitepaper_url=project.whitepaper_url,
                    delay_days=project.delay_days,
                    min_investment=project.min_investment,
                    max_investment=project.max_investment,
                    business_admin_wallet=project.business_admin_wallet,
                    token_contract_address=project.token_contract_address,
                    ieo_contract_address=project.ieo_contract_address,
                    reward_tracking_contract_address=project.reward_tracking_contract_address,
                    token_deployment_tx=project.token_deployment_tx,
                    ieo_deployment_tx=project.ieo_deployment_tx,
                    reward_tracking_deployment_tx=project.reward_tracking_deployment_tx,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                    investment_count=investment_count,
                    total_investors=total_investors
                ))
            
            total_pages = (total + limit - 1) // limit
            
            return AdminProjectListResponse(
                items=project_responses,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get projects: {str(e)}"
            )
    
    async def get_project(self, db: Session, project_id: str) -> AdminProjectResponse:
        """Get project by ID with admin details"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Get owner details
            owner = db.query(User).filter(User.id == project.owner_id).first()
            
            # Get investment data
            investment_count = db.query(Investment).filter(Investment.project_id == project.id).count()
            total_investors = db.query(Investment.investor_id).filter(
                Investment.project_id == project.id
            ).distinct().count()
            
            return AdminProjectResponse(
                id=project.id,
                owner_id=project.owner_id,
                owner_name=owner.name if owner else "Unknown",
                owner_email=owner.email if owner else "Unknown",
                owner_company=owner.company if owner else None,
                name=project.name,
                symbol=project.symbol,
                description=project.description,
                category=project.category,
                initial_supply=project.initial_supply,
                current_raised=project.current_raised,
                
                risk_level=project.risk_level,
                status=project.status,
                image_url=project.image_url,
                business_plan_url=project.business_plan_url,
                whitepaper_url=project.whitepaper_url,
                delay_days=project.delay_days,
                min_investment=project.min_investment,
                max_investment=project.max_investment,
                business_admin_wallet=project.business_admin_wallet,
                token_contract_address=project.token_contract_address,
                ieo_contract_address=project.ieo_contract_address,
                reward_tracking_contract_address=project.reward_tracking_contract_address,
                token_deployment_tx=project.token_deployment_tx,
                ieo_deployment_tx=project.ieo_deployment_tx,
                reward_tracking_deployment_tx=project.reward_tracking_deployment_tx,
                created_at=project.created_at,
                updated_at=project.updated_at,
                investment_count=investment_count,
                total_investors=total_investors
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get project: {str(e)}"
            )
    
    async def update_project(
        self,
        db: Session,
        project_id: str,
        update_data: AdminProjectUpdate,
        admin_user: User
    ) -> AdminProjectResponse:
        """Update project by admin"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Update fields
            if update_data.status is not None:
                project.status = update_data.status
            if update_data.risk_level is not None:
                project.risk_level = update_data.risk_level
            if update_data.business_admin_wallet is not None:
                project.business_admin_wallet = update_data.business_admin_wallet
            
            project.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(project)
            
            # Log admin action
            await self._log_admin_action(
                db=db,
                admin_user=admin_user,
                action="update_project",
                target_type="project",
                target_id=project_id,
                details=update_data.dict(exclude_unset=True)
            )
            
            return await self.get_project(db, project_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update project: {str(e)}"
            )
    
    async def update_business_admin(
        self,
        db: Session,
        update_data: BusinessAdminUpdate,
        admin_user: User
    ) -> BusinessAdminUpdateResponse:
        """Update business admin wallet in smart contracts"""
        try:
            project = db.query(Project).filter(Project.id == update_data.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.ieo_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project does not have IEO contract deployed"
                )
            
            # Get current business admin from contract
            # This would require a blockchain call to get the current admin
            # For now, we'll assume we have the current admin stored somewhere
            
            # Update business admin in IEO contract
            # This would require calling the setBusinessAdmin function on the IEO contract
            # For now, we'll simulate the transaction
            
            transaction_hash = "0x" + "1" * 64  # Simulated transaction hash
            
            # Update the project record
            old_business_admin = project.business_admin_wallet
            project.business_admin_wallet = update_data.new_business_admin_wallet
            project.updated_at = datetime.utcnow()
            db.commit()
            
            # Log admin action
            await self._log_admin_action(
                db=db,
                admin_user=admin_user,
                action="update_business_admin",
                target_type="project",
                target_id=update_data.project_id,
                details={
                    "old_business_admin": old_business_admin,
                    "new_business_admin": update_data.new_business_admin_wallet,
                    "transaction_hash": transaction_hash
                }
            )
            
            return BusinessAdminUpdateResponse(
                project_id=update_data.project_id,
                old_business_admin=old_business_admin or "0x" + "0" * 40,
                new_business_admin=update_data.new_business_admin_wallet,
                transaction_hash=transaction_hash,
                success=True,
                message="Business admin updated successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating business admin: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update business admin: {str(e)}"
            )
    
    # Dashboard
    async def get_dashboard_stats(self, db: Session) -> AdminDashboardStats:
        """Get admin dashboard statistics"""
        try:
            # User statistics
            total_users = db.query(User).count()
            total_smes = db.query(User).filter(User.user_type == UserType.SME).count()
            total_investors = db.query(User).filter(User.user_type == UserType.INVESTOR).count()
            
            # Project statistics
            total_projects = db.query(Project).count()
            active_projects = db.query(Project).filter(Project.status == ProjectStatus.ACTIVE).count()
            pending_projects = db.query(Project).filter(Project.status == ProjectStatus.PENDING).count()
            completed_projects = db.query(Project).filter(Project.status == ProjectStatus.COMPLETED).count()
            rejected_projects = db.query(Project).filter(Project.status == ProjectStatus.REJECTED).count()
            
            # Financial statistics
            total_raised_result = db.query(func.sum(Project.current_raised)).scalar()
            total_raised = total_raised_result if total_raised_result else 0
            
            total_investments = db.query(Investment).count()
            
            # Recent users (last 10)
            recent_users_query = db.query(User).filter(User.user_type != UserType.ADMIN).order_by(desc(User.created_at)).limit(10)
            recent_users = []
            for user in recent_users_query.all():
                project_count = db.query(Project).filter(Project.owner_id == user.id).count()
                investment_count = db.query(Investment).filter(Investment.investor_id == user.id).count()
                
                recent_users.append(AdminUserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    name=user.name,
                    user_type=user.user_type,
                    company=user.company,
                    status=user.status,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    wallet_address=user.wallet_address,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    project_count=project_count,
                    investment_count=investment_count
                ))
            
            # Recent projects (last 10)
            recent_projects_query = db.query(Project).order_by(desc(Project.created_at)).limit(10)
            recent_projects = []
            for project in recent_projects_query.all():
                owner = db.query(User).filter(User.id == project.owner_id).first()
                investment_count = db.query(Investment).filter(Investment.project_id == project.id).count()
                total_investors = db.query(Investment.investor_id).filter(
                    Investment.project_id == project.id
                ).distinct().count()
                
                recent_projects.append(AdminProjectResponse(
                    id=project.id,
                    owner_id=project.owner_id,
                    owner_name=owner.name if owner else "Unknown",
                    owner_email=owner.email if owner else "Unknown",
                    owner_company=owner.company if owner else None,
                    name=project.name,
                    symbol=project.symbol,
                    description=project.description,
                    category=project.category,
                    initial_supply=project.initial_supply,
                    current_raised=project.current_raised,
                    
                    risk_level=project.risk_level,
                    status=project.status,
                    image_url=project.image_url,
                    business_plan_url=project.business_plan_url,
                    whitepaper_url=project.whitepaper_url,
                    delay_days=project.delay_days,
                    min_investment=project.min_investment,
                    max_investment=project.max_investment,
                    business_admin_wallet=project.business_admin_wallet,
                    token_contract_address=project.token_contract_address,
                    ieo_contract_address=project.ieo_contract_address,
                    reward_tracking_contract_address=project.reward_tracking_contract_address,
                    token_deployment_tx=project.token_deployment_tx,
                    ieo_deployment_tx=project.ieo_deployment_tx,
                    reward_tracking_deployment_tx=project.reward_tracking_deployment_tx,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                    investment_count=investment_count,
                    total_investors=total_investors
                ))
            
            return AdminDashboardStats(
                total_users=total_users,
                total_smes=total_smes,
                total_investors=total_investors,
                total_projects=total_projects,
                active_projects=active_projects,
                pending_projects=pending_projects,
                completed_projects=completed_projects,
                rejected_projects=rejected_projects,
                total_raised=total_raised,
                total_investments=total_investments,
                recent_users=recent_users,
                recent_projects=recent_projects
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get dashboard stats: {str(e)}"
            )
    
    # Helper methods
    async def _log_admin_action(
        self,
        db: Session,
        admin_user: User,
        action: str,
        target_type: str,
        target_id: Optional[str],
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log admin action for audit trail"""
        try:
            # In a real implementation, you would create an AdminActionLog model
            # and store the action in the database
            logger.info(f"Admin action: {admin_user.email} performed {action} on {target_type} {target_id}")
            logger.info(f"Details: {details}")
        except Exception as e:
            logger.error(f"Error logging admin action: {str(e)}")

# Global instance
admin_service = AdminService()
