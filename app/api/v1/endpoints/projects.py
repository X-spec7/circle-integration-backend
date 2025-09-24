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
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Ensure user is SME
async def get_sme_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an SME"""
    if current_user.user_type != UserType.SME:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SME users can create projects"
        )
    return current_user

@router.post("/", response_model=ProjectDeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_sme_user),
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
    project_status: Optional[str] = None,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects with optional filtering (all authenticated users)
    """
    try:
        projects = await project_service.get_projects(
            db=db,
            status=project_status,
            category=category,
            risk_level=risk_level,
            skip=skip,
            limit=limit
        )
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get projects: {str(e)}"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID (all authenticated users)
    """
    try:
        project = await project_service.get_project_by_id(db=db, project_id=project_id)
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a project (project owner or admin only)
    """
    try:
        # Check if user is project owner or admin
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if current_user.id != project.owner_id and current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner or admin can update projects"
            )
        
        updated_project = await project_service.update_project(
            db=db,
            project_id=project_id,
            project_data=project_data
        )
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project (project owner or admin only)
    """
    try:
        # Check if user is project owner or admin
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if current_user.id != project.owner_id and current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner or admin can delete projects"
            )
        
        await project_service.delete_project(db=db, project_id=project_id)
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.post("/{project_id}/upload-image")
async def upload_project_image(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload project image (project owner or admin only)
    """
    try:
        # Check if user is project owner or admin
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if current_user.id != project.owner_id and current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner or admin can upload images"
            )
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Validate file size (max 5MB)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 5MB"
            )
        
        # In a real implementation, you would upload to a cloud storage service
        # For now, we'll just return a mock URL
        image_url = f"https://example.com/images/{project_id}/{file.filename}"
        
        # Update project with image URL
        project.image_url = image_url
        db.commit()
        
        return {"message": "Image uploaded successfully", "image_url": image_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )

@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project statistics (all authenticated users)
    """
    try:
        stats = await project_service.get_project_by_id_stats(db=db, project_id=project_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project stats: {str(e)}"
        )
