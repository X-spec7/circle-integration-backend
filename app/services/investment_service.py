"""
Investment Service for handling investor operations
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.investment import Investment, InvestmentStatus
from app.schemas.investment import (
    InvestmentCreate, InvestmentResponse, InvestmentListResponse,
    InvestmentStats, ClaimTokensRequest, RefundInvestmentRequest,
    ClaimTokensResponse, RefundInvestmentResponse, ProjectInvestmentInfo
)
from app.services.blockchain_service import blockchain_service

logger = logging.getLogger(__name__)

class InvestmentService:
    """Service for investment operations"""
    
    def __init__(self):
        self.blockchain_service = blockchain_service
    
    async def create_investment(
        self,
        db: Session,
        user: User,
        investment_data: InvestmentCreate
    ) -> InvestmentResponse:
        """Create a new investment"""
        try:
            # Get project
            project = db.query(Project).filter(Project.id == investment_data.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Validate project is active
            if project.status != ProjectStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project is not active for investments"
                )
            
            # Validate investment amount
            min_investment = Decimal(project.min_investment) / Decimal(1000000)  # Convert from 6 decimals
            max_investment = Decimal(project.max_investment) / Decimal(1000000)
            
            if investment_data.usdc_amount < min_investment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Investment amount must be at least ${min_investment}"
                )
            
            if investment_data.usdc_amount > max_investment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Investment amount must not exceed ${max_investment}"
                )
            
            # Convert USDC amount to 6 decimals for blockchain
            usdc_amount_6_decimals = int(investment_data.usdc_amount * Decimal(1000000))
            
            # Call blockchain to make investment
            try:
                # This would call the IEO contract's invest function
                # For now, we'll simulate the transaction
                transaction_hash = "0x" + "1" * 64  # Simulated transaction hash
                token_amount = investment_data.usdc_amount * Decimal(1000)  # Simulated token calculation
                
                # Create investment record
                investment = Investment(
                    investor_id=user.id,
                    project_id=investment_data.project_id,
                    usdc_amount=investment_data.usdc_amount,
                    token_amount=token_amount,
                    investment_time=datetime.utcnow(),
                    status=InvestmentStatus.CONFIRMED,
                    transaction_hash=transaction_hash
                )
                
                db.add(investment)
                db.commit()
                db.refresh(investment)
                
                # Update project raised amount
                project.current_raised = (project.current_raised or Decimal(0)) + investment_data.usdc_amount
                db.commit()
                
                return InvestmentResponse(
                    id=investment.id,
                    investor_id=investment.investor_id,
                    project_id=investment.project_id,
                    project_name=project.name,
                    project_symbol=project.symbol,
                    usdc_amount=investment.usdc_amount,
                    token_amount=investment.token_amount,
                    investment_time=investment.investment_time,
                    status=investment.status,
                    claimed=investment.claimed,
                    refunded=investment.refunded,
                    claimable=False,  # Would check against claim delay
                    refundable=True,  # Would check against refund period
                    claim_delay_hours=project.delay_days * 24,
                    refund_period_hours=project.delay_days * 24,
                    transaction_hash=investment.transaction_hash,
                    created_at=investment.created_at,
                    updated_at=investment.updated_at
                )
                
            except Exception as e:
                logger.error(f"Blockchain investment failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Investment failed: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating investment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create investment: {str(e)}"
            )
    
    async def get_user_investments(
        self,
        db: Session,
        user_id: str,
        page: int = 1,
        limit: int = 50,
        project_id: Optional[str] = None
    ) -> InvestmentListResponse:
        """Get user's investments with pagination"""
        try:
            query = db.query(Investment).join(Project).filter(Investment.investor_id == user_id)
            
            if project_id:
                query = query.filter(Investment.project_id == project_id)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            investments = query.offset(offset).limit(limit).all()
            
            # Convert to response format
            investment_responses = []
            for investment in investments:
                project = db.query(Project).filter(Project.id == investment.project_id).first()
                
                # Check if claimable and refundable
                claim_delay = timedelta(hours=project.delay_days * 24)
                refund_period = timedelta(hours=project.delay_days * 24)
                
                now = datetime.utcnow()
                investment_time = investment.investment_time
                
                claimable = (not investment.claimed and not investment.refunded and 
                           now >= investment_time + claim_delay)
                refundable = (not investment.claimed and not investment.refunded and 
                            now <= investment_time + refund_period)
                
                investment_responses.append(InvestmentResponse(
                    id=investment.id,
                    investor_id=investment.investor_id,
                    project_id=investment.project_id,
                    project_name=project.name if project else "Unknown",
                    project_symbol=project.symbol if project else "UNK",
                    usdc_amount=investment.usdc_amount,
                    token_amount=investment.token_amount,
                    investment_time=investment.investment_time,
                    status=investment.status,
                    claimed=investment.claimed,
                    refunded=investment.refunded,
                    claimable=claimable,
                    refundable=refundable,
                    claim_delay_hours=project.delay_days * 24 if project else 0,
                    refund_period_hours=project.delay_days * 24 if project else 0,
                    transaction_hash=investment.transaction_hash,
                    created_at=investment.created_at,
                    updated_at=investment.updated_at
                ))
            
            total_pages = (total + limit - 1) // limit
            
            return InvestmentListResponse(
                items=investment_responses,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error getting user investments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get investments: {str(e)}"
            )
    
    async def get_investment(
        self,
        db: Session,
        investment_id: str,
        user_id: str
    ) -> InvestmentResponse:
        """Get specific investment details"""
        try:
            investment = db.query(Investment).filter(
                Investment.id == investment_id,
                Investment.investor_id == user_id
            ).first()
            
            if not investment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Investment not found"
                )
            
            project = db.query(Project).filter(Project.id == investment.project_id).first()
            
            # Check if claimable and refundable
            claim_delay = timedelta(hours=project.delay_days * 24)
            refund_period = timedelta(hours=project.delay_days * 24)
            
            now = datetime.utcnow()
            investment_time = investment.investment_time
            
            claimable = (not investment.claimed and not investment.refunded and 
                       now >= investment_time + claim_delay)
            refundable = (not investment.claimed and not investment.refunded and 
                        now <= investment_time + refund_period)
            
            return InvestmentResponse(
                id=investment.id,
                investor_id=investment.investor_id,
                project_id=investment.project_id,
                project_name=project.name if project else "Unknown",
                project_symbol=project.symbol if project else "UNK",
                usdc_amount=investment.usdc_amount,
                token_amount=investment.token_amount,
                investment_time=investment.investment_time,
                status=investment.status,
                claimed=investment.claimed,
                refunded=investment.refunded,
                claimable=claimable,
                refundable=refundable,
                claim_delay_hours=project.delay_days * 24 if project else 0,
                refund_period_hours=project.delay_days * 24 if project else 0,
                transaction_hash=investment.transaction_hash,
                created_at=investment.created_at,
                updated_at=investment.updated_at
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting investment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get investment: {str(e)}"
            )
    
    async def claim_tokens(
        self,
        db: Session,
        user: User,
        claim_data: ClaimTokensRequest
    ) -> ClaimTokensResponse:
        """Claim tokens for investments"""
        try:
            # This would call the IEO contract's claimTokens function
            # For now, we'll simulate the transaction
            transaction_hash = "0x" + "2" * 64  # Simulated transaction hash
            
            # Update investment records
            query = db.query(Investment).filter(Investment.investor_id == user.id)
            if claim_data.project_id:
                query = query.filter(Investment.project_id == claim_data.project_id)
            
            investments = query.filter(
                Investment.claimed == False,
                Investment.refunded == False
            ).all()
            
            total_tokens_claimed = Decimal(0)
            for investment in investments:
                investment.claimed = True
                investment.status = InvestmentStatus.CLAIMED
                total_tokens_claimed += investment.token_amount
            
            db.commit()
            
            return ClaimTokensResponse(
                project_id=claim_data.project_id or "all",
                tokens_claimed=total_tokens_claimed,
                transaction_hash=transaction_hash,
                success=True,
                message="Tokens claimed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error claiming tokens: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to claim tokens: {str(e)}"
            )
    
    async def refund_investment(
        self,
        db: Session,
        user: User,
        refund_data: RefundInvestmentRequest
    ) -> RefundInvestmentResponse:
        """Refund an investment"""
        try:
            # This would call the IEO contract's refund function
            # For now, we'll simulate the transaction
            transaction_hash = "0x" + "3" * 64  # Simulated transaction hash
            
            query = db.query(Investment).filter(
                Investment.investor_id == user.id,
                Investment.project_id == refund_data.project_id
            )
            
            if refund_data.investment_index is not None:
                investments = query.all()
                if refund_data.investment_index >= len(investments):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Investment index out of bounds"
                    )
                investments = [investments[refund_data.investment_index]]
            else:
                investments = query.filter(
                    Investment.claimed == False,
                    Investment.refunded == False
                ).all()
            
            total_usdc_refunded = Decimal(0)
            for investment in investments:
                investment.refunded = True
                investment.status = InvestmentStatus.REFUNDED
                total_usdc_refunded += investment.usdc_amount
                
                # Update project raised amount
                project = db.query(Project).filter(Project.id == investment.project_id).first()
                if project:
                    project.current_raised = (project.current_raised or Decimal(0)) - investment.usdc_amount
            
            db.commit()
            
            return RefundInvestmentResponse(
                project_id=refund_data.project_id,
                usdc_refunded=total_usdc_refunded,
                transaction_hash=transaction_hash,
                success=True,
                message="Investment refunded successfully"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refunding investment: {str(e)}")
            # db.rollback()  # SQLAlchemy handles rollback automatically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refund investment: {str(e)}"
            )
    
    async def get_user_investment_stats(
        self,
        db: Session,
        user_id: str
    ) -> InvestmentStats:
        """Get investment statistics for user"""
        try:
            investments = db.query(Investment).filter(Investment.investor_id == user_id).all()
            
            total_investments = len(investments)
            total_usdc_invested = sum(inv.usdc_amount for inv in investments)
            total_tokens_received = sum(inv.token_amount for inv in investments)
            total_claimed = sum(inv.token_amount for inv in investments if inv.claimed)
            total_refunded = sum(inv.usdc_amount for inv in investments if inv.refunded)
            active_investments = len([inv for inv in investments if not inv.claimed and not inv.refunded])
            
            # Calculate claimable and refundable
            now = datetime.utcnow()
            claimable_investments = 0
            refundable_investments = 0
            
            for investment in investments:
                if investment.claimed or investment.refunded:
                    continue
                
                project = db.query(Project).filter(Project.id == investment.project_id).first()
                if not project:
                    continue
                
                claim_delay = timedelta(hours=project.delay_days * 24)
                refund_period = timedelta(hours=project.delay_days * 24)
                
                if now >= investment.investment_time + claim_delay:
                    claimable_investments += 1
                
                if now <= investment.investment_time + refund_period:
                    refundable_investments += 1
            
            return InvestmentStats(
                total_investments=total_investments,
                total_usdc_invested=total_usdc_invested,
                total_tokens_received=total_tokens_received,
                total_claimed=total_claimed,
                total_refunded=total_refunded,
                active_investments=active_investments,
                claimable_investments=claimable_investments,
                refundable_investments=refundable_investments
            )
            
        except Exception as e:
            logger.error(f"Error getting investment stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get investment stats: {str(e)}"
            )
    
    async def get_project_investment_info(
        self,
        db: Session,
        project_id: str,
        user_id: str
    ) -> ProjectInvestmentInfo:
        """Get investment information for a specific project"""
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Get user's investments in this project
            user_investments = db.query(Investment).filter(
                Investment.investor_id == user_id,
                Investment.project_id == project_id
            ).all()
            
            user_investment_count = len(user_investments)
            user_total_invested = sum(inv.usdc_amount for inv in user_investments)
            user_total_tokens = sum(inv.token_amount for inv in user_investments)
            
            # Calculate claimable and refundable
            now = datetime.utcnow()
            claim_delay = timedelta(hours=project.delay_days * 24)
            refund_period = timedelta(hours=project.delay_days * 24)
            
            user_claimable_tokens = Decimal(0)
            user_refundable_amount = Decimal(0)
            
            for investment in user_investments:
                if investment.claimed or investment.refunded:
                    continue
                
                if now >= investment.investment_time + claim_delay:
                    user_claimable_tokens += investment.token_amount
                
                if now <= investment.investment_time + refund_period:
                    user_refundable_amount += investment.usdc_amount
            
            return ProjectInvestmentInfo(
                project_id=project.id,
                project_name=project.name,
                project_symbol=project.symbol,
                is_ieo_active=project.status == ProjectStatus.ACTIVE,
                min_investment=Decimal(project.min_investment) / Decimal(1000000),
                max_investment=Decimal(project.max_investment) / Decimal(1000000),
                total_raised=project.current_raised or Decimal(0),
                total_tokens_sold=Decimal(0),  # Would get from blockchain
                user_investment_count=user_investment_count,
                user_total_invested=user_total_invested,
                user_total_tokens=user_total_tokens,
                user_claimable_tokens=user_claimable_tokens,
                user_refundable_amount=user_refundable_amount,
                claim_delay_hours=project.delay_days * 24,
                refund_period_hours=project.delay_days * 24,
                token_price=None,  # Would get from price oracle
                price_timestamp=None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting project investment info: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get project investment info: {str(e)}"
            )

# Global instance
investment_service = InvestmentService()
