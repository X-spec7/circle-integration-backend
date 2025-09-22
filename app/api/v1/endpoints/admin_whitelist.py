from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project
from app.schemas.admin import WhitelistAddRequest, WhitelistRemoveRequest, WhitelistResponse
from app.services.blockchain_service import blockchain_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this endpoint"
        )
    return current_user

@router.post("/projects/{project_id}/whitelist/add", response_model=WhitelistResponse)
async def add_to_whitelist(
    project_id: str,
    whitelist_data: WhitelistAddRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Add an address to a project's whitelist"""
    try:
        logger.info(f"👤 Admin {current_user.email} adding {whitelist_data.address} to whitelist for project {project_id}")
        
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not project.token_contract_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project token contract not deployed"
            )
        
        # Add to whitelist via smart contract
        tx_hash = await blockchain_service.add_to_whitelist(
            token_contract_address=project.token_contract_address,
            address=whitelist_data.address
        )
        
        logger.info(f"✅ Address {whitelist_data.address} added to whitelist for project {project_id}")
        return WhitelistResponse(
            project_id=project_id,
            address=whitelist_data.address,
            action="added",
            transaction_hash=tx_hash,
            message=f"Address {whitelist_data.address} added to whitelist successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding to whitelist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add address to whitelist"
        )

@router.post("/projects/{project_id}/whitelist/remove", response_model=WhitelistResponse)
async def remove_from_whitelist(
    project_id: str,
    whitelist_data: WhitelistRemoveRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Remove an address from a project's whitelist"""
    try:
        logger.info(f"👤 Admin {current_user.email} removing {whitelist_data.address} from whitelist for project {project_id}")
        
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not project.token_contract_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project token contract not deployed"
            )
        
        # Remove from whitelist via smart contract
        tx_hash = await blockchain_service.remove_from_whitelist(
            token_contract_address=project.token_contract_address,
            address=whitelist_data.address
        )
        
        logger.info(f"✅ Address {whitelist_data.address} removed from whitelist for project {project_id}")
        return WhitelistResponse(
            project_id=project_id,
            address=whitelist_data.address,
            action="removed",
            transaction_hash=tx_hash,
            message=f"Address {whitelist_data.address} removed from whitelist successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error removing from whitelist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove address from whitelist"
        )

@router.post("/projects/{project_id}/whitelist/batch-add", response_model=List[WhitelistResponse])
async def batch_add_to_whitelist(
    project_id: str,
    addresses: List[str],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Add multiple addresses to a project's whitelist"""
    try:
        logger.info(f"👤 Admin {current_user.email} batch adding {len(addresses)} addresses to whitelist for project {project_id}")
        
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not project.token_contract_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project token contract not deployed"
            )
        
        # Batch add to whitelist via smart contract
        tx_hash = await blockchain_service.batch_add_to_whitelist(
            token_contract_address=project.token_contract_address,
            addresses=addresses
        )
        
        logger.info(f"✅ {len(addresses)} addresses added to whitelist for project {project_id}")
        
        # Return individual responses for each address
        responses = []
        for address in addresses:
            responses.append(WhitelistResponse(
                project_id=project_id,
                address=address,
                action="added",
                transaction_hash=tx_hash,
                message=f"Address {address} added to whitelist successfully"
            ))
        
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error batch adding to whitelist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to batch add addresses to whitelist"
        )

@router.get("/projects/{project_id}/whitelist/check/{address}")
async def check_whitelist_status(
    project_id: str,
    address: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Check if an address is whitelisted for a project"""
    try:
        logger.info(f"👤 Admin {current_user.email} checking whitelist status for {address} in project {project_id}")
        
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not project.token_contract_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project token contract not deployed"
            )
        
        # Check whitelist status via smart contract
        is_whitelisted = await blockchain_service.is_whitelisted(
            token_contract_address=project.token_contract_address,
            address=address
        )
        
        logger.info(f"✅ Whitelist status checked for {address}: {is_whitelisted}")
        return {
            "project_id": project_id,
            "address": address,
            "is_whitelisted": is_whitelisted,
            "message": f"Address {address} is {'whitelisted' if is_whitelisted else 'not whitelisted'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error checking whitelist status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check whitelist status"
        )
