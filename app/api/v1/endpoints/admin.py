"""
Admin API endpoints for user and project management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.schemas.admin import (
    AdminUserResponse, AdminUserUpdate, AdminUserListResponse,
    AdminProjectResponse, AdminProjectUpdate, AdminProjectListResponse,
    AdminDashboardStats, BusinessAdminUpdate, BusinessAdminUpdateResponse,
    AdminUserFilters, AdminProjectFilters
)
from app.services.admin_service import admin_service

router = APIRouter()

# Admin authentication dependency
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Dashboard
@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    return await admin_service.get_dashboard_stats(db)

# User Management
@router.get("/users", response_model=AdminUserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    user_type: Optional[UserType] = Query(None, description="Filter by user type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name, email, username, company"),
    created_from: Optional[datetime] = Query(None, description="Filter by creation date from"),
    created_to: Optional[datetime] = Query(None, description="Filter by creation date to"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of users with filters"""
    filters = AdminUserFilters(
        user_type=user_type,
        status=status,
        is_active=is_active,
        search=search,
        created_from=created_from,
        created_to=created_to
    )
    return await admin_service.get_users(db, filters, page, limit)

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID with admin details"""
    return await admin_service.get_user(db, user_id)

@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: str,
    user_data: AdminUserUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user by admin"""
    return await admin_service.update_user(db, user_id, user_data, current_user)

# Project Management
@router.get("/projects", response_model=AdminProjectListResponse)
async def get_projects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by project status"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    category: Optional[str] = Query(None, description="Filter by category"),
    owner_id: Optional[str] = Query(None, description="Filter by owner ID"),
    search: Optional[str] = Query(None, description="Search in name, symbol, description"),
    created_from: Optional[datetime] = Query(None, description="Filter by creation date from"),
    created_to: Optional[datetime] = Query(None, description="Filter by creation date to"),
    raised_min: Optional[float] = Query(None, description="Filter by minimum raised amount"),
    raised_max: Optional[float] = Query(None, description="Filter by maximum raised amount"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of projects with filters"""
    filters = AdminProjectFilters(
        status=status,
        risk_level=risk_level,
        category=category,
        owner_id=owner_id,
        search=search,
        created_from=created_from,
        created_to=created_to,
        raised_min=raised_min,
        raised_max=raised_max
    )
    return await admin_service.get_projects(db, filters, page, limit)

@router.get("/projects/{project_id}", response_model=AdminProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get project by ID with admin details"""
    return await admin_service.get_project(db, project_id)

@router.put("/projects/{project_id}", response_model=AdminProjectResponse)
async def update_project(
    project_id: str,
    project_data: AdminProjectUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update project by admin"""
    return await admin_service.update_project(db, project_id, project_data, current_user)

# Business Admin Management
@router.put("/projects/{project_id}/business-admin", response_model=BusinessAdminUpdateResponse)
async def update_business_admin(
    project_id: str,
    business_admin_data: BusinessAdminUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update business admin wallet in smart contracts"""
    business_admin_data.project_id = project_id
    return await admin_service.update_business_admin(db, business_admin_data, current_user)

# System Management
@router.get("/system/settings")
async def get_system_settings(
    current_user: User = Depends(get_admin_user)
):
    """Get system settings"""
    # In a real implementation, you would fetch from database
    return {
        "maintenance_mode": False,
        "new_user_registration": True,
        "new_project_creation": True,
        "min_investment_amount": 100,
        "max_investment_amount": 1000000,
        "default_delay_days": 7
    }

@router.put("/system/settings")
async def update_system_settings(
    settings_data: dict,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update system settings"""
    # In a real implementation, you would update database
    return {
        "message": "System settings updated successfully",
        "settings": settings_data
    }

# Audit Logs
@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(None, description="Filter by action"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    admin_id: Optional[str] = Query(None, description="Filter by admin ID"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin action audit logs"""
    # In a real implementation, you would fetch from AdminActionLog table
    return {
        "items": [],
        "total": 0,
        "page": page,
        "limit": limit,
        "total_pages": 0
    }
