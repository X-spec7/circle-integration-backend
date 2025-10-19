import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models.docsign import DocumentSigning, DocumentSigner, DocumentSigningStatus
from app.services.document_signing_providers import (
    DocumentSigningProvider,
    DocumentSigningRequest,
    Signer,
    SignatureField,
    SigningStatus,
)


class DocumentSigningService:
    def __init__(self, db: Session, provider: DocumentSigningProvider):
        self.db = db
        self.provider = provider
        self.logger = logging.getLogger(__name__)

    def create_document_signing_request(
        self,
        user_id: str,
        document_name: str,
        document_path: str,
        document_type: str,
        signers_data: List[Dict[str, Any]],
        project_id: Optional[str] = None,
        investment_id: Optional[str] = None,
        signature_fields: Optional[List[Dict[str, Any]]] = None,
        subject: Optional[str] = None,
        message: Optional[str] = None,
    ) -> DocumentSigning:
        signers = [Signer(email=s["email"], name=s["name"], role=s.get("role", "signer"), order=s.get("order", 1)) for s in signers_data]
        fields = []
        for f in signature_fields or []:
            fields.append(SignatureField(page=f["page"], x=f["x"], y=f["y"], width=f.get("width", 0), height=f.get("height", 0)))

        req = DocumentSigningRequest(
            document_name=document_name,
            document_path=document_path,
            signers=signers,
            signature_fields=fields,
            subject=subject or f"Please sign {document_name}",
            message=message or f"Please review and sign the attached {document_name} document.",
        )

        resp = self.provider.create_envelope(req)
        if resp.error_message:
            raise RuntimeError(resp.error_message)

        doc = DocumentSigning(
            envelope_id=resp.envelope_id,
            document_name=document_name,
            document_path=document_path,
            document_type=document_type,
            status=DocumentSigningStatus(resp.status.value),
            signing_service=self.provider.__class__.__name__.lower().replace("provider", ""),
            user_id=user_id,
            project_id=project_id,
            investment_id=investment_id,
        )
        self.db.add(doc)
        self.db.flush()
        for s in signers:
            ds = DocumentSigner(
                document_signing_id=doc.id,
                email=s.email,
                name=s.name,
                role=s.role,
                signer_order=s.order,
            )
            self.db.add(ds)
        self.db.commit()
        self.db.refresh(doc)
        self.logger.info("Document signing request created", extra={"doc_id": doc.id, "envelope_id": doc.envelope_id})
        return doc

    def get_document_signing_status(self, envelope_id: str) -> DocumentSigningStatus:
        status = self.provider.get_envelope_status(envelope_id)
        return DocumentSigningStatus(status.value)

    def update_document_signing_status(self, envelope_id: str) -> None:
        doc: Optional[DocumentSigning] = self.db.query(DocumentSigning).filter(DocumentSigning.envelope_id == envelope_id).first()
        if not doc:
            return
        new_status = self.get_document_signing_status(envelope_id)
        doc.status = new_status
        if new_status == DocumentSigningStatus.SIGNED:
            doc.signed_at = datetime.utcnow()
        doc.updated_at = datetime.utcnow()
        self.db.commit()
        self.logger.info("Document signing status updated", extra={"envelope_id": envelope_id, "status": new_status.value})

    def download_signed_document(self, envelope_id: str) -> bytes:
        return self.provider.download_signed_document(envelope_id)

    def cancel_document_signing(self, envelope_id: str) -> bool:
        ok = self.provider.cancel_envelope(envelope_id)
        if ok:
            doc: Optional[DocumentSigning] = self.db.query(DocumentSigning).filter(DocumentSigning.envelope_id == envelope_id).first()
            if doc:
                doc.status = DocumentSigningStatus.CANCELLED
                doc.updated_at = datetime.utcnow()
                self.db.commit()
        return ok

    def get_user_document_signing_requests(self, user_id: str) -> List[DocumentSigning]:
        return (
            self.db.query(DocumentSigning)
            .filter(DocumentSigning.user_id == user_id)
            .order_by(DocumentSigning.created_at.desc())
            .all()
        )

    def get_project_documents(self, project_id: str) -> List[DocumentSigning]:
        return self.db.query(DocumentSigning).filter(DocumentSigning.project_id == project_id).all()


