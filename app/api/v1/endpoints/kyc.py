import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.kyc import KycClientCreate, KycClientOut, KycSessionCreate
from app.services.kyc_service import KycService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create-client", response_model=KycClientOut)
def create_kyc_client(
    payload: KycClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        service = KycService(db)
        kyc_client = service.create_kyc_client(
            user=current_user,
            client_type=payload.client_type,
            entity_name=payload.entity_name,
            email=payload.email,
        )
        return kyc_client
    except Exception as e:
        logger.exception("create_kyc_client failed")
        raise HTTPException(status_code=500, detail="Failed to create KYC client")


@router.post("/create-session/{complycube_client_id}")
def create_verification_session(
    complycube_client_id: str,
    payload: KycSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        service = KycService(db)
        session_data = service.create_verification_session(
            complycube_client_id=complycube_client_id,
            redirect_url=payload.redirect_url,
            webhook_url=payload.webhook_url,
            session_type=payload.session_type or "document_check",
        )
        return {"id": session_data.get("id"), "session_url": session_data.get("sessionUrl")}
    except Exception as e:
        logger.exception("create_verification_session failed")
        raise HTTPException(status_code=500, detail="Failed to create verification session")


@router.get("/status")
def get_kyc_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = KycService(db)
    kyc = service.get_user_kyc(current_user.id)
    if not kyc:
        return {"success": False, "message": "No KYC record found"}
    return {
        "success": True,
        "complycube_client_id": kyc.complycube_client_id,
        "status": kyc.status,
        "status_text": kyc.status_text,
        "created_at": kyc.created_at,
        "updated_at": kyc.updated_at,
    }


@router.get("/download-document/{document_id}")
def download_document(
    document_id: str,
    side: str = "front",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = KycService(db)
    data = service.download_document(document_id, side)
    if "decoded_data" in data:
        return Response(
            content=data["decoded_data"],
            media_type=data.get("contentType", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename={data.get('fileName', 'document')}"
            },
        )
    logger.warning("download_document not found", extra={"document_id": document_id, "side": side})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.post("/manual-review/{complycube_client_id}")
def manual_review(
    complycube_client_id: str,
    action: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = KycService(db)
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'")
    ok = service.manual_review(complycube_client_id, action)
    return {"success": ok}


