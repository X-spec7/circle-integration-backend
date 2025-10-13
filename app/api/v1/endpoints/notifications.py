from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserType
from app.schemas.notification import (
    NotificationCreate,
    NotificationSettingsUpdate,
    NotificationSettingsOut,
)
from app.services.notification_service import notification_service


router = APIRouter()


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != UserType.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/send", status_code=status.HTTP_202_ACCEPTED)
async def send_notifications(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    count = await notification_service.send_notifications(db, data)
    return {"sent": count}


@router.put("/settings", response_model=NotificationSettingsOut)
def update_settings(
    data: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.notifications_enabled = data.notifications_enabled
    db.commit()
    return {"notifications_enabled": current_user.notifications_enabled}

