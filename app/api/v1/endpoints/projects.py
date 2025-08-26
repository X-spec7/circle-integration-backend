from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project, ProjectStatus, RiskLevel
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList
from app.services.user_service import UserService
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project (SME users only)
    """
    if current_user.user_type != UserType.SME:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SME users can create projects"
        )
    
    # Create project
    project = Project(
        id=str(uuid.uuid4()),
        owner_id=current_user.id,
        name=project_data.name,
        symbol=project_data.symbol,
        description=project_data.description,
        category=project_data.category,
        target_amount=project_data.target_amount,
        price_per_token=project_data.price_per_token,
        total_supply=project_data.total_supply,
        end_date=project_data.end_date,
        risk_level=project_data.risk_level,
        status=ProjectStatus.PENDING,
        image_url=project_data.image_url,
        business_plan_url=project_data.business_plan_url,
        whitepaper_url=project_data.whitepaper_url
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

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
    project = db.query(Project).filter(Project.id == project_id).first()
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
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project"
        )
    
    # Update project fields
    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    
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
    project = db.query(Project).filter(Project.id == project_id).first()
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
    
    project = db.query(Project).filter(Project.id == project_id).first()
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
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.status = ProjectStatus.REJECTED
    project.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Project rejected", "reason": reason} 