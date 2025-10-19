import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models.kyc import KycClient, KycStatus, KycPersonalDetails, KycCompanyDetails, KycDocument
from app.models.user import User
from app.services.complycube_client import ComplyCubeClient


class KycService:
    def __init__(self, db: Session):
        self.db = db
        self.client = ComplyCubeClient()
        self.logger = logging.getLogger(__name__)

    def create_kyc_client(self, user: User, client_type: str, entity_name: str, email: str) -> KycClient:
        self.logger.info(
            "KYC create_kyc_client",
            extra={"user_id": user.id, "client_type": client_type, "entity_name": entity_name, "email": email},
        )
        payload = {"type": client_type, "email": email, "entityName": entity_name}
        resp = self.client.create_client(payload)
        complycube_client_id = resp.get("id")

        kyc_client = KycClient(
            complycube_client_id=complycube_client_id,
            user_id=user.id,
            client_type=client_type,
            entity_name=entity_name,
            email=email,
            status=KycStatus.NOT_STARTED,
        )
        self.db.add(kyc_client)
        self.db.commit()
        self.db.refresh(kyc_client)
        self.logger.info("KYC client created", extra={"kyc_id": kyc_client.id, "cc_client_id": complycube_client_id})
        return kyc_client

    def create_verification_session(self, complycube_client_id: str, redirect_url: str, webhook_url: str,
                                    session_type: str = "document_check") -> Dict[str, Any]:
        session_payload = {
            "type": session_type,
            "redirectUrl": redirect_url,
            "webhookUrl": webhook_url,
        }
        self.logger.info(
            "KYC create_verification_session",
            extra={"cc_client_id": complycube_client_id, "session_type": session_type},
        )
        return self.client.create_verification_session(complycube_client_id, session_payload)

    def get_user_kyc(self, user_id: str) -> Optional[KycClient]:
        return self.db.query(KycClient).filter(KycClient.user_id == user_id).first()

    def download_document(self, document_id: str, side: str = "front") -> Dict[str, Any]:
        self.logger.info("KYC download_document", extra={"document_id": document_id, "side": side})
        data = self.client.download_document(document_id, side)
        if "data" in data:
            try:
                data["decoded_data"] = base64.b64decode(data["data"])  # bytes
            except Exception:
                pass
        return data

    def update_verification_status(self, complycube_client_id: str, status: KycStatus, status_text: str) -> None:
        kyc_client: Optional[KycClient] = (
            self.db.query(KycClient)
            .filter(KycClient.complycube_client_id == complycube_client_id)
            .first()
        )
        if not kyc_client:
            self.logger.warning("KYC update status: client not found", extra={"cc_client_id": complycube_client_id})
            return

        kyc_client.status = status
        kyc_client.status_text = status_text

        user: Optional[User] = self.db.query(User).filter(User.id == kyc_client.user_id).first()
        if user:
            user.kyc_verified = status == KycStatus.VERIFIED

        self.db.commit()
        self.logger.info(
            "KYC status updated",
            extra={"cc_client_id": complycube_client_id, "status": str(status), "user_id": kyc_client.user_id},
        )

    def manual_review(self, complycube_client_id: str, action: str) -> bool:
        if action not in ["approve", "reject"]:
            return False
        status = KycStatus.VERIFIED if action == "approve" else KycStatus.DECLINED
        status_text = "KYC Verified by Admin" if action == "approve" else "KYC Rejected by Admin"
        self.logger.info("KYC manual_review", extra={"cc_client_id": complycube_client_id, "action": action})
        self.update_verification_status(complycube_client_id, status, status_text)
        return True


