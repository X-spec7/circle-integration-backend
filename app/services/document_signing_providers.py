import base64
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import requests

from app.core.config import settings


class SigningStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class Signer:
    email: str
    name: str
    role: str = "signer"
    order: int = 1


@dataclass
class SignatureField:
    page: int
    x: float
    y: float
    width: float
    height: float
    field_type: str = "signature"


@dataclass
class DocumentSigningRequest:
    document_name: str
    document_path: str
    signers: List[Signer]
    signature_fields: List[SignatureField]
    subject: str
    message: str
    callback_url: Optional[str] = None


@dataclass
class DocumentSigningResponse:
    envelope_id: str
    status: SigningStatus
    signing_url: Optional[str] = None
    error_message: Optional[str] = None


class DocumentSigningProvider:
    def create_envelope(self, request: DocumentSigningRequest) -> DocumentSigningResponse:
        raise NotImplementedError

    def get_envelope_status(self, envelope_id: str) -> SigningStatus:
        raise NotImplementedError

    def download_signed_document(self, envelope_id: str) -> bytes:
        raise NotImplementedError

    def cancel_envelope(self, envelope_id: str) -> bool:
        raise NotImplementedError


class DocuSignProvider(DocumentSigningProvider):
    def __init__(self):
        self.client_id = settings.docusign_client_id
        self.client_secret = settings.docusign_client_secret
        self.account_id = settings.docusign_account_id
        self.base_url = settings.docusign_base_url.rstrip("/")
        self.access_token: Optional[str] = None
        self.logger = logging.getLogger(__name__)

    def _get_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        auth_url = f"{self.base_url}/oauth/token"
        data = {"grant_type": "client_credentials", "scope": "signature impersonation"}
        resp = requests.post(auth_url, data=data, auth=(self.client_id, self.client_secret), headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code == 200:
            self.access_token = resp.json()["access_token"]
            return self.access_token
        raise RuntimeError(f"DocuSign auth failed: {resp.text}")

    def _headers(self):
        return {"Authorization": f"Bearer {self._get_access_token()}", "Content-Type": "application/json"}

    def create_envelope(self, request: DocumentSigningRequest) -> DocumentSigningResponse:
        try:
            with open(request.document_path, "rb") as f:
                content_b64 = base64.b64encode(f.read()).decode("utf-8")
            envelope = {
                "emailSubject": request.subject,
                "emailBlurb": request.message,
                "documents": [{
                    "documentBase64": content_b64,
                    "name": request.document_name,
                    "fileExtension": "pdf",
                    "documentId": "1"
                }],
                "recipients": {"signers": []},
                "status": "sent",
            }
            for i, s in enumerate(request.signers):
                signer = {
                    "email": s.email,
                    "name": s.name,
                    "recipientId": str(i + 1),
                    "routingOrder": s.order,
                    "tabs": {"signHereTabs": []},
                }
                for field in request.signature_fields:
                    if field.field_type == "signature":
                        signer["tabs"]["signHereTabs"].append({
                            "documentId": "1",
                            "pageNumber": field.page,
                            "xPosition": field.x,
                            "yPosition": field.y,
                        })
                envelope["recipients"]["signers"].append(signer)
            url = f"{self.base_url}/accounts/{self.account_id}/envelopes"
            resp = requests.post(url, json=envelope, headers=self._headers())
            if resp.status_code in (200, 201):
                data = resp.json()
                return DocumentSigningResponse(envelope_id=data.get("envelopeId", ""), status=SigningStatus.SENT, signing_url=data.get("uri"))
            return DocumentSigningResponse(envelope_id="", status=SigningStatus.DRAFT, error_message=resp.text)
        except Exception as e:
            self.logger.exception("DocuSign create_envelope failed")
            return DocumentSigningResponse(envelope_id="", status=SigningStatus.DRAFT, error_message=str(e))

    def get_envelope_status(self, envelope_id: str) -> SigningStatus:
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}"
            resp = requests.get(url, headers=self._headers())
            if resp.status_code == 200:
                status = (resp.json().get("status") or "draft").lower()
                return SigningStatus(status)
        except Exception:
            self.logger.exception("DocuSign get_envelope_status failed")
        return SigningStatus.DRAFT

    def download_signed_document(self, envelope_id: str) -> bytes:
        url = f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}/documents/combined"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code == 200:
            return resp.content
        raise RuntimeError(f"Failed to download document: {resp.text}")

    def cancel_envelope(self, envelope_id: str) -> bool:
        url = f"{self.base_url}/accounts/{self.account_id}/envelopes/{envelope_id}"
        payload = {"status": "voided", "voidedReason": "Cancelled by system"}
        resp = requests.put(url, json=payload, headers=self._headers())
        return resp.status_code == 200


