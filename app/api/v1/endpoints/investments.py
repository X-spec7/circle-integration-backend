from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.models.project import Project, ProjectStatus
from app.models.investment import Investment, InvestmentStatus
from app.models.whitelist_request import WhitelistRequest, WhitelistRequestStatus, WhitelistRequestAddress
from app.schemas.investment import InvestmentCreate, InvestmentResponse, InvestmentDetail
from app.schemas.project import ProjectResponse
from app.schemas.business_admin import InvestorWhitelistApplyRequest, InvestorWhitelistApplyResponse, WhitelistRequestItem, WhitelistRequestListResponse
from app.services.investment_service import InvestmentService
from app.services.blockchain_service import blockchain_service
import logging
from pydantic import BaseModel

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
        
        # Annotate whitelist flag
        for p in projects:
            count = db.query(WhitelistRequest).filter(WhitelistRequest.project_id == p.id, WhitelistRequest.status == WhitelistRequestStatus.PENDING).count()
            setattr(p, "has_whitelist_request", count > 0)
        
        logger.info(f"✅ Found {len(projects)} projects for investor")
        return projects
        
    except Exception as e:
        logger.error(f"❌ Error getting available projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.post("/whitelist/apply", response_model=InvestorWhitelistApplyResponse)
async def apply_whitelist(
    data: InvestorWhitelistApplyRequest,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Investor applies to be whitelisted for a project with one or more addresses (requires KYC-verified)."""
    try:
        # Enforce KYC verification (support legacy is_verified)
        if not getattr(current_user, "kyc_verified", getattr(current_user, "is_verified", False)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KYC verification required")
        
        project = db.query(Project).filter(Project.id == data.project_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
        addresses_clean = [a.strip() for a in data.addresses if a and a.strip()]
        if not addresses_clean:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid addresses provided")
        
        # Check duplicates per address (pending only) using address table
        dup = db.query(WhitelistRequestAddress).filter(
            WhitelistRequestAddress.project_id == project.id,
            WhitelistRequestAddress.address.in_(addresses_clean),
            WhitelistRequestAddress.status == WhitelistRequestStatus.PENDING
        ).first()
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Address already has a pending request for this project: {dup.address}")
        
        req = WhitelistRequest(
            project_id=project.id,
            investor_id=current_user.id,
            addresses=",".join(addresses_clean),
            status=WhitelistRequestStatus.PENDING
        )
        db.add(req)
        db.flush()
        
        # Insert per-address rows
        for addr in addresses_clean:
            db.add(WhitelistRequestAddress(
                request_id=req.id,
                project_id=project.id,
                investor_id=current_user.id,
                address=addr,
                status=WhitelistRequestStatus.PENDING
            ))
        db.commit()
        db.refresh(req)
        
        return InvestorWhitelistApplyResponse(
            request_id=req.id,
            project_id=req.project_id,
            addresses=addresses_clean,
            status=req.status,
            created_at=req.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error applying for whitelist: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to apply for whitelist")

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

# NOTE: not used anymore!
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
        if project.token_contract_address and current_user.wallet_address:
            is_whitelisted = await blockchain_service.is_whitelisted(
                token_contract_address=project.token_contract_address,
                address=current_user.wallet_address
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

@router.get("/whitelist/requests", response_model=WhitelistRequestListResponse)
async def list_my_whitelist_requests(
    project_id: str = Query(...),
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """List current investor's whitelist requests for a project."""
    reqs = db.query(WhitelistRequest).filter(
        WhitelistRequest.project_id == project_id,
        WhitelistRequest.investor_id == current_user.id
    ).order_by(WhitelistRequest.created_at.desc()).all()

    items: List[WhitelistRequestItem] = []
    for r in reqs:
        addresses = [a.strip() for a in (r.addresses or '').split(',') if a.strip()]
        items.append(WhitelistRequestItem(
            id=r.id,
            investor_id=current_user.id,
            applicant_name=None,
            addresses=addresses,
            status=r.status.value if hasattr(r.status, 'value') else str(r.status),
            created_at=r.created_at
        ))
    return WhitelistRequestListResponse(items=items, total=len(items))

class InvestorUpdateWhitelistStatusRequest(BaseModel):
    status: str

@router.post("/whitelist/requests/{request_id}/status")
async def update_my_whitelist_request_status(
    request_id: str,
    body: InvestorUpdateWhitelistStatusRequest,
    current_user: User = Depends(get_investor_user),
    db: Session = Depends(get_db)
):
    """Allow investor to change a rejected whitelist request back to pending (re-apply)."""
    # Only allow setting to pending
    if body.status.lower() != WhitelistRequestStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only status 'pending' is allowed")

    # Fetch request and verify ownership
    req = db.query(WhitelistRequest).filter(WhitelistRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Whitelist request not found")
    if req.investor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your request")

    # Only from rejected -> pending
    current_status = req.status.value if hasattr(req.status, 'value') else str(req.status)
    if current_status != WhitelistRequestStatus.REJECTED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only rejected requests can be re-applied")

    # Check duplicates per address before switching to pending
    child_rows = db.query(WhitelistRequestAddress).filter(WhitelistRequestAddress.request_id == req.id).all()
    addresses = [cr.address for cr in child_rows]
    if addresses:
        dup = db.query(WhitelistRequestAddress).filter(
            WhitelistRequestAddress.project_id == req.project_id,
            WhitelistRequestAddress.address.in_(addresses),
            WhitelistRequestAddress.status == WhitelistRequestStatus.PENDING,
            WhitelistRequestAddress.request_id != req.id
        ).first()
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Address already has a pending request for this project: {dup.address}")

    # Update statuses
    req.status = WhitelistRequestStatus.PENDING
    db.query(WhitelistRequestAddress).filter(WhitelistRequestAddress.request_id == req.id).update({
        'status': WhitelistRequestStatus.PENDING
    })
    db.commit()

    return {"request_id": req.id, "project_id": req.project_id, "status": req.status.value}
