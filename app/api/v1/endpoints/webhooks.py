import hmac
import hashlib
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.kyc_service import KycService
from app.models.kyc import KycStatus


router = APIRouter()


def verify_signature(secret: str, payload: bytes, signature: Optional[str]) -> bool:
    if not signature:
        return False
    computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    # ComplyCube may send signature as hex; adjust if format differs
    return hmac.compare_digest(computed, signature)


@router.post("/complycube")
async def complycube_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(default=None, alias="X-Signature"),
):
    raw = await request.body()
    if settings.complycube_webhook_secret:
        if not verify_signature(settings.complycube_webhook_secret, raw, x_signature):
            raise HTTPException(status_code=401, detail="invalid signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    logging.info(f"ComplyCube webhook: {json.dumps(payload)}")

    event_type = payload.get("type")
    client_id = payload.get("clientId") or payload.get("client_id")
    status_text = payload.get("statusText") or payload.get("status_text") or ""

    if not client_id:
        return {"success": True}

    service = KycService(db)

    if event_type == "verification.completed":
        # Map payload status to our enum if provided
        status_str = payload.get("status")
        status_map = {
            "verified": KycStatus.VERIFIED,
            "declined": KycStatus.DECLINED,
            "review": KycStatus.REVIEW,
        }
        status = status_map.get((status_str or "").lower(), KycStatus.REVIEW)
        service.update_verification_status(client_id, status, status_text)

    # other events can be handled if needed

    return {"success": True}


