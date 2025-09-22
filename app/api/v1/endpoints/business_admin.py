"""
Business Admin API endpoints for project management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project
from app.schemas.business_admin import (
    StartIEORequest, EndIEORequest, WithdrawUSDCRequest, WithdrawAllUSDCRequest,
    IEOStatusResponse, WithdrawalResponse, ProjectStatsResponse,
    WhitelistUserRequest, WhitelistBatchRequest, WhitelistResponse
)
from app.services.business_admin_service import business_admin_service

router = APIRouter()

# Ensure user is business admin
async def get_business_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a business admin"""
    if current_user.user_type != UserType.BUSINESS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business admins can access this endpoint"
        )
    return current_user


# Ensure user is business admin for a project
async def verify_business_admin_access(
    project_id: str,
    current_user: User,
    db: Session
) -> Project:
    """Verify current user has business admin access to the project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is the project owner or has business admin wallet
    if (current_user.id != project.owner_id and 
        current_user.wallet_address != project.business_admin_wallet):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or business admin can access this endpoint"
        )
    return project

@router.post("/projects/{project_id}/start-ieo")
async def start_ieo(
    project_id: str,
    start_data: StartIEORequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start the IEO for a project"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.start_ieo(db, project_id, start_data)

@router.post("/projects/{project_id}/end-ieo")
async def end_ieo(
    project_id: str,
    end_data: EndIEORequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End the IEO for a project"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.end_ieo(db, project_id, end_data)

@router.get("/projects/{project_id}/ieo-status")
async def get_ieo_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get IEO status for a project"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.get_ieo_status(db, project_id)

@router.post("/projects/{project_id}/withdraw-usdc")
async def withdraw_usdc(
    project_id: str,
    withdrawal_data: WithdrawUSDCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Withdraw USDC from IEO contract"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.withdraw_usdc(db, project_id, withdrawal_data)

@router.post("/projects/{project_id}/withdraw-all-usdc")
async def withdraw_all_usdc(
    project_id: str,
    withdrawal_data: WithdrawAllUSDCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Withdraw all USDC from IEO contract"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.withdraw_all_usdc(db, project_id, withdrawal_data)

@router.get("/projects/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project statistics"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.get_project_stats(db, project_id)

@router.post("/projects/{project_id}/whitelist/user")
async def whitelist_user(
    project_id: str,
    whitelist_data: WhitelistUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Whitelist a single user for the project"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.whitelist_user(db, project_id, whitelist_data)

@router.post("/projects/{project_id}/whitelist/batch")
async def whitelist_batch(
    project_id: str,
    whitelist_data: WhitelistBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Whitelist multiple users for the project"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.whitelist_batch(db, project_id, whitelist_data)

@router.get("/projects/{project_id}/whitelist")
async def get_whitelist(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get whitelisted users for the project"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.get_whitelist(db, project_id)

@router.delete("/projects/{project_id}/whitelist/{user_address}")
async def remove_from_whitelist(
    project_id: str,
    user_address: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove user from whitelist"""
    await verify_business_admin_access(project_id, current_user, db)
    return await business_admin_service.remove_from_whitelist(db, project_id, user_address)

@router.get("/projects")
async def get_business_admin_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Get projects where current user is business admin"""
    return await business_admin_service.get_business_admin_projects(db, current_user, page, limit)

@router.post("/projects/{project_id}/set-oracle")
async def set_oracle_address(
    project_id: str,
    oracle_data: dict,
    current_user: User = Depends(get_business_admin_user),
    db: Session = Depends(get_db)
):
    """Set oracle address for a project's IEO contract"""
    try:
        logger.info(f"🔮 Business admin {current_user.email} setting oracle for project {project_id}")
        
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not project.ieo_contract_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IEO contract not deployed for this project"
            )
        
        # Set oracle address via smart contract
        tx_hash = await blockchain_service.set_oracle_address(
            ieo_contract_address=project.ieo_contract_address,
            oracle_address=oracle_data['oracle_address']
        )
        
        logger.info(f"✅ Oracle address set for project {project_id}: {tx_hash}")
        return {
            "project_id": project_id,
            "oracle_address": oracle_data['oracle_address'],
            "transaction_hash": tx_hash,
            "message": "Oracle address set successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error setting oracle address: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set oracle address"
        )

