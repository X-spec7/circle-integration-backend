from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project, ProjectStatus
from app.models.investment import Investment, InvestmentStatus
from app.schemas.investment import InvestmentCreate, InvestmentResponse, InvestmentDetail
from app.schemas.project import ProjectResponse
from app.services.investment_service import InvestmentService
from app.services.blockchain_service import blockchain_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_investor_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an investor"""
    if current_user.user_type != UserType.INVESTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only investors can access this endpoint"
        )
    return current_user

@router.get("/projects", response_model=List[ProjectResponse])
async def get_available_projects(
    project_status: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get all available projects for investment"""
    try:
        logger.info(f"📋 Investor {current_user.email} requesting available projects")
        
        # Filter projects by status and category
        query = db.query(Project)
        
        if project_status:
            query = query.filter(Project.status == project_status)
        else:
            # Only show active projects by default
            query = query.filter(Project.status == ProjectStatus.ACTIVE)
        
        if category:
            query = query.filter(Project.category == category)
        
        projects = query.all()
        
        logger.info(f"✅ Found {len(projects)} projects for investor")
        return projects
        
    except Exception as e:
        logger.error(f"❌ Error getting available projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_details(
    project_id: str,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific project"""
    try:
        logger.info(f"📋 Investor {current_user.email} requesting project {project_id}")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        logger.info(f"✅ Project details retrieved for {project_id}")
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting project details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project details"
        )

@router.post("/invest", response_model=InvestmentResponse)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Create a new investment in a project"""
    try:
        logger.info(f"💰 Investor {current_user.email} creating investment in project {investment_data.project_id}")
        
        # Verify project exists and is active
        project = db.query(Project).filter(Project.id == investment_data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.status != ProjectStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project is not available for investment"
            )
        
        # Check if investor is whitelisted
        # Note: This would require checking the smart contract whitelist
        # For now, we'll assume all investors are whitelisted
        
        # Validate investment amount
        if investment_data.amount < project.min_investment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Investment amount must be at least {project.min_investment} USDC"
            )
        
        if investment_data.amount > project.max_investment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Investment amount cannot exceed {project.max_investment} USDC"
            )
        
        # Create investment record
        investment_service = InvestmentService(db)
        investment = await investment_service.create_investment(
            investor_id=current_user.id,
            project_id=investment_data.project_id,
            amount=investment_data.amount,
            payment_method=investment_data.payment_method
        )
        
        logger.info(f"✅ Investment created: {investment.id}")
        return investment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating investment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create investment"
        )

@router.get("/my-investments", response_model=List[InvestmentDetail])
async def get_my_investments(
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get all investments made by the current investor"""
    try:
        logger.info(f"📋 Getting investments for investor {current_user.email}")
        
        investment_service = InvestmentService(db)
        investments = await investment_service.get_investor_investments(current_user.id)
        
        logger.info(f"✅ Found {len(investments)} investments for investor")
        return investments
        
    except Exception as e:
        logger.error(f"❌ Error getting investor investments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investments"
        )

@router.get("/investments/{investment_id}", response_model=InvestmentDetail)
async def get_investment_details(
    investment_id: str,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific investment"""
    try:
        logger.info(f"📋 Getting investment details for {investment_id}")
        
        investment_service = InvestmentService(db)
        investment = await investment_service.get_investment_by_id(investment_id)
        
        if not investment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investment not found"
            )
        
        # Verify the investment belongs to the current user
        if investment.investor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this investment"
            )
        
        logger.info(f"✅ Investment details retrieved for {investment_id}")
        return investment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting investment details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve investment details"
        )

@router.post("/investments/{investment_id}/claim")
async def claim_tokens(
    investment_id: str,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Claim tokens for a completed investment"""
    try:
        logger.info(f"🎁 Investor {current_user.email} claiming tokens for investment {investment_id}")
        
        investment_service = InvestmentService(db)
        result = await investment_service.claim_tokens(investment_id, current_user.id)
        
        logger.info(f"✅ Tokens claimed successfully for investment {investment_id}")
        return {"message": "Tokens claimed successfully", "transaction_hash": result.get("tx_hash")}
        
    except Exception as e:
        logger.error(f"❌ Error claiming tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to claim tokens"
        )

@router.post("/investments/{investment_id}/refund")
async def request_refund(
    investment_id: str,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Request a refund for an investment"""
    try:
        logger.info(f"💸 Investor {current_user.email} requesting refund for investment {investment_id}")
        
        investment_service = InvestmentService(db)
        result = await investment_service.request_refund(investment_id, current_user.id)
        
        logger.info(f"✅ Refund requested successfully for investment {investment_id}")
        return {"message": "Refund requested successfully", "transaction_hash": result.get("tx_hash")}
        
    except Exception as e:
        logger.error(f"❌ Error requesting refund: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request refund"
        )

@router.post("/crypto-invest", response_model=InvestmentResponse)
async def create_crypto_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Create a crypto investment in a project"""
    try:
        logger.info(f"💰 Investor {current_user.email} creating crypto investment in project {investment_data.project_id}")
        
        # Verify project exists and is active
        project = db.query(Project).filter(Project.id == investment_data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.status != ProjectStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project is not available for investment"
            )
        
        # Check if investor is whitelisted
        if project.token_contract_address:
            is_whitelisted = await blockchain_service.is_whitelisted(
                token_contract_address=project.token_contract_address,
                address=current_user.wallet_address or ""
            )
            if not is_whitelisted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Investor address not whitelisted for this project"
                )
        
        # Validate investment amount
        if investment_data.amount < project.min_investment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Investment amount must be at least {project.min_investment} USDC"
            )
        
        if investment_data.amount > project.max_investment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Investment amount cannot exceed {project.max_investment} USDC"
            )
        
        # Create investment record
        investment_service = InvestmentService(db)
        investment = await investment_service.create_investment(
            investor_id=current_user.id,
            project_id=investment_data.project_id,
            amount=investment_data.amount,
            payment_method=investment_data.payment_method
        )
        
        logger.info(f"✅ Crypto investment created: {investment.id}")
        return investment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating crypto investment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create crypto investment"
        )
