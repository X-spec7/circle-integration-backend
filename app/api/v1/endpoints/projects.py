from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project, ProjectStatus, RiskLevel
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList, ProjectDeploymentResponse
from app.services.user_service import UserService
from app.services.project_service import project_service
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=ProjectDeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project with ERC20 token and escrow contract deployment (SME users only)
    """
    try:
        deployment_response = await project_service.create_project(
            db=db,
            user=current_user,
            project_data=project_data
        )
        return deployment_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    status: Optional[ProjectStatus] = None,
    category: Optional[str] = None,
    risk_level: Optional[RiskLevel] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of projects with optional filtering
    """
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    if category:
        query = query.filter(Project.category == category)
    if risk_level:
        query = query.filter(Project.risk_level == risk_level)
    
    # Only show active projects to public
    query = query.filter(Project.status == ProjectStatus.ACTIVE)
    
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get specific project details
    """
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only show active projects to public
    if project.status != ProjectStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project (owner only)
    """
    update_data = project_data.dict(exclude_unset=True)
    project = await project_service.update_project(
        db=db,
        project_id=project_id,
        user=current_user,
        update_data=update_data
    )
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project (owner only)
    """
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

@router.get("/user/projects", response_model=List[ProjectResponse])
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's projects
    """
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

@router.get("/{project_id}/escrow-address")
async def get_project_escrow_address(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get escrow address for a project
    """
    escrow_address = await project_service.get_escrow_address(db, project_id)
    if not escrow_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or escrow address not found"
        )
    
    return {"escrow_address": escrow_address}

# Admin endpoints for project approval
@router.post("/{project_id}/approve")
async def approve_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a project (admin only)
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can approve projects"
        )
    
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.status = ProjectStatus.ACTIVE
    project.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Project approved successfully"}

@router.post("/{project_id}/reject")
async def reject_project(
    project_id: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a project (admin only)
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can reject projects"
        )
    
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.status = ProjectStatus.REJECTED
    project.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Project rejected", "reason": reason} 