"""
Investment API endpoints for investors
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project
from app.models.investment import Investment
from app.schemas.investment import (
    InvestmentCreate, InvestmentResponse, InvestmentListResponse,
    InvestmentStats, ClaimTokensRequest, RefundInvestmentRequest
)
from app.services.investment_service import investment_service

router = APIRouter()

# Ensure user is investor
async def get_investor_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an investor"""
    if current_user.user_type != UserType.INVESTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only investors can access investment endpoints"
        )
    return current_user

@router.post("/invest", response_model=InvestmentResponse)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Make an investment in a project"""
    return await investment_service.create_investment(db, current_user, investment_data)

@router.get("/my-investments", response_model=InvestmentListResponse)
async def get_my_investments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get current user's investments"""
    return await investment_service.get_user_investments(
        db, current_user.id, page, limit, project_id
    )

@router.get("/investments/{investment_id}", response_model=InvestmentResponse)
async def get_investment(
    investment_id: str,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get specific investment details"""
    return await investment_service.get_investment(db, investment_id, current_user.id)

@router.post("/claim-tokens")
async def claim_tokens(
    claim_data: ClaimTokensRequest,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Claim tokens for investments that have passed the claim delay"""
    return await investment_service.claim_tokens(db, current_user, claim_data)

@router.post("/refund-investment")
async def refund_investment(
    refund_data: RefundInvestmentRequest,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Refund a specific investment within the refund period"""
    return await investment_service.refund_investment(db, current_user, refund_data)

@router.get("/investment-stats", response_model=InvestmentStats)
async def get_investment_stats(
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get investment statistics for current user"""
    return await investment_service.get_user_investment_stats(db, current_user.id)

@router.get("/projects/{project_id}/investment-info")
async def get_project_investment_info(
    project_id: str,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get investment information for a specific project"""
    return await investment_service.get_project_investment_info(db, project_id, current_user.id)
