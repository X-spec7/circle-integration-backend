import os
import tempfile
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.docsign import DocumentSigning, DocumentSigningStatus
from app.services.document_signing_service import DocumentSigningService
from app.services.document_signing_providers import DocuSignProvider


router = APIRouter()
logger = logging.getLogger(__name__)


def get_provider():
    # For now, we use DocuSignProvider based on settings
    return DocuSignProvider()


@router.post("/upload-and-sign")
async def upload_and_sign_document(
    document_type: str,
    signers: List[dict],
    project_id: Optional[str] = None,
    investment_id: Optional[str] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        service = DocumentSigningService(db, get_provider())
        doc = service.create_document_signing_request(
            user_id=current_user.id,
            document_name=file.filename,
            document_path=temp_file_path,
            document_type=document_type,
            signers_data=signers,
            project_id=project_id,
            investment_id=investment_id,
        )

        try:
            os.unlink(temp_file_path)
        except Exception:
            pass

        return {"success": True, "envelope_id": doc.envelope_id, "status": doc.status.value}
    except Exception:
        logger.exception("upload_and_sign_document failed")
        raise HTTPException(status_code=500, detail="Failed to create signing request")


@router.get("/{envelope_id}/status")
def get_document_status(
    envelope_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DocumentSigningService(db, get_provider())
    service.update_document_signing_status(envelope_id)
    doc: Optional[DocumentSigning] = db.query(DocumentSigning).filter(DocumentSigning.envelope_id == envelope_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "envelope_id": envelope_id, "status": doc.status.value, "signed_at": doc.signed_at, "created_at": doc.created_at}


@router.get("/{envelope_id}/download")
def download_signed_document(
    envelope_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    doc: Optional[DocumentSigning] = db.query(DocumentSigning).filter(DocumentSigning.envelope_id == envelope_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != DocumentSigningStatus.SIGNED:
        raise HTTPException(status_code=400, detail="Document is not signed yet")
    service = DocumentSigningService(db, get_provider())
    content = service.download_signed_document(envelope_id)
    return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=signed_{doc.document_name}"})


@router.post("/{envelope_id}/cancel")
def cancel_document_signing(
    envelope_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DocumentSigningService(db, get_provider())
    ok = service.cancel_document_signing(envelope_id)
    return {"success": ok}


@router.get("/me")
def list_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DocumentSigningService(db, get_provider())
    docs = service.get_user_document_signing_requests(current_user.id)
    return {
        "success": True,
        "documents": [
            {
                "id": d.id,
                "envelope_id": d.envelope_id,
                "document_name": d.document_name,
                "document_type": d.document_type,
                "status": d.status.value,
                "created_at": d.created_at,
                "signed_at": d.signed_at,
            }
            for d in docs
        ],
    }


