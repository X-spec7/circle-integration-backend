"""
Business Admin Service for handling project management operations
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from fastapi import HTTPException, status
from datetime import datetime
from decimal import Decimal

from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.business_admin import (
    StartIEORequest, EndIEORequest, WithdrawUSDCRequest, WithdrawAllUSDCRequest,
    IEOStatusResponse, WithdrawalResponse, ProjectStatsResponse,
    WhitelistUserRequest, WhitelistBatchRequest, WhitelistResponse
)
from app.services.blockchain_service import blockchain_service

logger = logging.getLogger(__name__)

class BusinessAdminService:
    """Service for business admin operations"""
    
    def __init__(self):
        self.blockchain_service = blockchain_service
    
    async def start_ieo(
        self,
        db: Session,
        project_id: str,
        start_data: StartIEORequest
    ) -> dict:
        """Start the IEO for a project"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.ieo_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IEO contract not deployed"
                )
            
            # Call blockchain to start IEO
            try:
                transaction_hash = await self.blockchain_service.start_ieo(
                    ieo_contract_address=project.ieo_contract_address,
                    price_oracle_address=start_data.price_oracle_address
                )
                
                return {
                    "project_id": project_id,
                    "transaction_hash": transaction_hash,
                    "success": True,
                    "message": "IEO started successfully"
                }
                
            except Exception as e:
                logger.error(f"Blockchain start IEO failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to start IEO: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting IEO: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start IEO: {str(e)}"
            )
    
    async def end_ieo(
        self,
        db: Session,
        project_id: str,
        end_data: EndIEORequest
    ) -> dict:
        """End the IEO for a project"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.ieo_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IEO contract not deployed"
                )
            
            # Call blockchain to end IEO
            try:
                transaction_hash = await self.blockchain_service.end_ieo(
                    ieo_contract_address=project.ieo_contract_address
                )
                
                return {
                    "project_id": project_id,
                    "transaction_hash": transaction_hash,
                    "success": True,
                    "message": "IEO ended successfully"
                }
                
            except Exception as e:
                logger.error(f"Blockchain end IEO failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to end IEO: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error ending IEO: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to end IEO: {str(e)}"
            )
    
    async def get_ieo_status(
        self,
        db: Session,
        project_id: str
    ) -> IEOStatusResponse:
        """Get IEO status and statistics"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.ieo_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IEO contract not deployed"
                )
            
            # Get IEO status from blockchain
            try:
                ieo_status = await self.blockchain_service.get_ieo_status(
                    ieo_contract_address=project.ieo_contract_address
                )
                
                return IEOStatusResponse(
                    project_id=project_id,
                    is_active=ieo_status.get("is_active", False),
                    is_paused=ieo_status.get("is_paused", False),
                    start_time=ieo_status.get("start_time"),
                    total_raised=Decimal(ieo_status.get("total_raised", 0)) / Decimal(1000000),
                    total_tokens_sold=Decimal(ieo_status.get("total_tokens_sold", 0)) / Decimal(1000000000000000000),
                    total_deposited=Decimal(ieo_status.get("total_deposited", 0)) / Decimal(1000000),
                    total_withdrawn=Decimal(ieo_status.get("total_withdrawn", 0)) / Decimal(1000000),
                    withdrawable_amount=Decimal(ieo_status.get("withdrawable_amount", 0)) / Decimal(1000000),
                    investment_count=ieo_status.get("investment_count", 0),
                    investor_count=ieo_status.get("investor_count", 0),
                    min_investment=Decimal(project.min_investment) / Decimal(1000000),
                    max_investment=Decimal(project.max_investment) / Decimal(1000000),
                    claim_delay_hours=project.delay_days * 24,
                    refund_period_hours=project.delay_days * 24,
                    withdrawal_delay_hours=project.delay_days * 24
                )
                
            except Exception as e:
                logger.error(f"Blockchain get IEO status failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get IEO status: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting IEO status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get IEO status: {str(e)}"
            )
    
    async def withdraw_usdc(
        self,
        db: Session,
        project_id: str,
        withdraw_data: WithdrawUSDCRequest
    ) -> WithdrawalResponse:
        """Withdraw specific amount of USDC from project"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.ieo_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IEO contract not deployed"
                )
            
            # Convert USDC amount to 6 decimals
            usdc_amount_6_decimals = int(withdraw_data.amount * Decimal(1000000))
            
            # Call blockchain to withdraw USDC
            try:
                transaction_hash = await self.blockchain_service.withdraw_usdc(
                    ieo_contract_address=project.ieo_contract_address,
                    amount=usdc_amount_6_decimals
                )
                
                # Get remaining balance
                ieo_status = await self.blockchain_service.get_ieo_status(
                    ieo_contract_address=project.ieo_contract_address
                )
                remaining_balance = Decimal(ieo_status.get("withdrawable_amount", 0)) / Decimal(1000000)
                
                return WithdrawalResponse(
                    project_id=project_id,
                    amount_withdrawn=withdraw_data.amount,
                    transaction_hash=transaction_hash,
                    success=True,
                    message="USDC withdrawn successfully",
                    remaining_balance=remaining_balance
                )
                
            except Exception as e:
                logger.error(f"Blockchain withdraw USDC failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to withdraw USDC: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error withdrawing USDC: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to withdraw USDC: {str(e)}"
            )
    
    async def withdraw_all_usdc(
        self,
        db: Session,
        project_id: str,
        withdraw_data: WithdrawAllUSDCRequest
    ) -> WithdrawalResponse:
        """Withdraw all available USDC from project"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.ieo_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IEO contract not deployed"
                )
            
            # Call blockchain to withdraw all USDC
            try:
                transaction_hash = await self.blockchain_service.withdraw_all_usdc(
                    ieo_contract_address=project.ieo_contract_address
                )
                
                # Get remaining balance (should be 0)
                ieo_status = await self.blockchain_service.get_ieo_status(
                    ieo_contract_address=project.ieo_contract_address
                )
                remaining_balance = Decimal(ieo_status.get("withdrawable_amount", 0)) / Decimal(1000000)
                
                return WithdrawalResponse(
                    project_id=project_id,
                    amount_withdrawn=Decimal(0),  # Will be calculated by blockchain
                    transaction_hash=transaction_hash,
                    success=True,
                    message="All USDC withdrawn successfully",
                    remaining_balance=remaining_balance
                )
                
            except Exception as e:
                logger.error(f"Blockchain withdraw all USDC failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to withdraw all USDC: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error withdrawing all USDC: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to withdraw all USDC: {str(e)}"
            )
    
    async def get_project_stats(
        self,
        db: Session,
        project_id: str
    ) -> ProjectStatsResponse:
        """Get detailed project statistics"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Get IEO status from blockchain
            ieo_status = {}
            if project.ieo_contract_address:
                try:
                    ieo_status = await self.blockchain_service.get_ieo_status(
                        ieo_contract_address=project.ieo_contract_address
                    )
                except Exception as e:
                    logger.warning(f"Failed to get IEO status: {str(e)}")
            
            return ProjectStatsResponse(
                project_id=project.id,
                project_name=project.name,
                project_symbol=project.symbol,
                total_raised=project.current_raised or Decimal(0),
                total_tokens_sold=Decimal(ieo_status.get("total_tokens_sold", 0)) / Decimal(1000000000000000000),
                total_deposited=Decimal(ieo_status.get("total_deposited", 0)) / Decimal(1000000),
                total_withdrawn=Decimal(ieo_status.get("total_withdrawn", 0)) / Decimal(1000000),
                withdrawable_amount=Decimal(ieo_status.get("withdrawable_amount", 0)) / Decimal(1000000),
                investment_count=ieo_status.get("investment_count", 0),
                unique_investors=ieo_status.get("investor_count", 0),
                average_investment=Decimal(0),  # Would calculate from blockchain data
                largest_investment=Decimal(0),  # Would get from blockchain data
                smallest_investment=Decimal(0),  # Would get from blockchain data
                is_ieo_active=ieo_status.get("is_active", False),
                is_paused=ieo_status.get("is_paused", False),
                start_time=ieo_status.get("start_time"),
                created_at=project.created_at
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting project stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get project stats: {str(e)}"
            )
    
    async def add_to_whitelist(
        self,
        db: Session,
        project_id: str,
        whitelist_data: WhitelistUserRequest
    ) -> WhitelistResponse:
        """Add user to project token whitelist"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.token_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token contract not deployed"
                )
            
            # Call blockchain to add to whitelist
            try:
                transaction_hash = await self.blockchain_service.add_to_whitelist(
                    token_contract_address=project.token_contract_address,
                    wallet_address=whitelist_data.wallet_address
                )
                
                return WhitelistResponse(
                    project_id=project_id,
                    operation="add",
                    wallet_addresses=[whitelist_data.wallet_address],
                    transaction_hash=transaction_hash,
                    success=True,
                    message="User added to whitelist successfully"
                )
                
            except Exception as e:
                logger.error(f"Blockchain add to whitelist failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to add to whitelist: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding to whitelist: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to whitelist: {str(e)}"
            )
    
    async def batch_add_to_whitelist(
        self,
        db: Session,
        project_id: str,
        whitelist_data: WhitelistBatchRequest
    ) -> WhitelistResponse:
        """Add multiple users to project token whitelist"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.token_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token contract not deployed"
                )
            
            # Call blockchain to batch add to whitelist
            try:
                transaction_hash = await self.blockchain_service.batch_add_to_whitelist(
                    token_contract_address=project.token_contract_address,
                    wallet_addresses=whitelist_data.wallet_addresses
                )
                
                return WhitelistResponse(
                    project_id=project_id,
                    operation="batch_add",
                    wallet_addresses=whitelist_data.wallet_addresses,
                    transaction_hash=transaction_hash,
                    success=True,
                    message="Users added to whitelist successfully"
                )
                
            except Exception as e:
                logger.error(f"Blockchain batch add to whitelist failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to add to whitelist: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error batch adding to whitelist: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add to whitelist: {str(e)}"
            )
    
    async def remove_from_whitelist(
        self,
        db: Session,
        project_id: str,
        whitelist_data: WhitelistUserRequest
    ) -> WhitelistResponse:
        """Remove user from project token whitelist"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.token_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token contract not deployed"
                )
            
            # Call blockchain to remove from whitelist
            try:
                transaction_hash = await self.blockchain_service.remove_from_whitelist(
                    token_contract_address=project.token_contract_address,
                    wallet_address=whitelist_data.wallet_address
                )
                
                return WhitelistResponse(
                    project_id=project_id,
                    operation="remove",
                    wallet_addresses=[whitelist_data.wallet_address],
                    transaction_hash=transaction_hash,
                    success=True,
                    message="User removed from whitelist successfully"
                )
                
            except Exception as e:
                logger.error(f"Blockchain remove from whitelist failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to remove from whitelist: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing from whitelist: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove from whitelist: {str(e)}"
            )
    
    async def batch_remove_from_whitelist(
        self,
        db: Session,
        project_id: str,
        whitelist_data: WhitelistBatchRequest
    ) -> WhitelistResponse:
        """Remove multiple users from project token whitelist"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.token_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token contract not deployed"
                )
            
            # Call blockchain to batch remove from whitelist
            try:
                transaction_hash = await self.blockchain_service.batch_remove_from_whitelist(
                    token_contract_address=project.token_contract_address,
                    wallet_addresses=whitelist_data.wallet_addresses
                )
                
                return WhitelistResponse(
                    project_id=project_id,
                    operation="batch_remove",
                    wallet_addresses=whitelist_data.wallet_addresses,
                    transaction_hash=transaction_hash,
                    success=True,
                    message="Users removed from whitelist successfully"
                )
                
            except Exception as e:
                logger.error(f"Blockchain batch remove from whitelist failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to remove from whitelist: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error batch removing from whitelist: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove from whitelist: {str(e)}"
            )
    
    async def get_whitelist(
        self,
        db: Session,
        project_id: str,
        page: int = 1,
        limit: int = 100
    ) -> dict:
        """Get project token whitelist"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if not project.token_contract_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token contract not deployed"
                )
            
            # Get whitelist from blockchain
            try:
                whitelist_data = await self.blockchain_service.get_whitelist(
                    token_contract_address=project.token_contract_address,
                    page=page,
                    limit=limit
                )
                
                return {
                    "project_id": project_id,
                    "whitelisted_addresses": whitelist_data.get("addresses", []),
                    "total_count": whitelist_data.get("total_count", 0),
                    "page": page,
                    "limit": limit,
                    "total_pages": (whitelist_data.get("total_count", 0) + limit - 1) // limit
                }
                
            except Exception as e:
                logger.error(f"Blockchain get whitelist failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get whitelist: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting whitelist: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get whitelist: {str(e)}"
            )

# Global instance
business_admin_service = BusinessAdminService()
