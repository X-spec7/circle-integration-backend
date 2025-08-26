from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.services.user_service import UserService
from app.schemas.user import User, UserUpdate, UserProfile
from app.models.user import User, UserType

router = APIRouter()

@router.get("/me", response_model=UserProfile)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile
    """
    return current_user

@router.get("/profile", response_model=UserProfile)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile (alternative endpoint)
    """
    return current_user

@router.put("/me", response_model=UserProfile)
def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    updated_user = UserService.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.get("/", response_model=List[UserProfile])
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    user_type: UserType = Query(None, description="Filter by user type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of users with pagination and optional filtering
    """
    if user_type:
        users = UserService.get_users_by_type(db, user_type)
    else:
        users = UserService.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserProfile)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user (soft delete)
    """
    success = UserService.delete_user(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        ) 