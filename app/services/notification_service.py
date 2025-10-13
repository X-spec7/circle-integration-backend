from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User, UserType
from app.schemas.notification import NotificationCreate
from app.services.pubsub_broker import broker
from app.services.websocket_manager import ws_manager


NOTIF_CHANNEL_PREFIX = "notif:user:"


class NotificationService:
    def _resolve_target_users(self, db: Session, user_ids: Optional[List[str]], user_type: Optional[UserType]) -> List[User]:
        q = db.query(User).filter(User.is_active == True)  # noqa: E712
        if user_ids:
            q = q.filter(User.id.in_(user_ids))
        elif user_type:
            q = q.filter(User.user_type == user_type)
        else:
            q = q.filter(False)
        return q.all()

    async def send_notifications(self, db: Session, data: NotificationCreate) -> int:
        users = self._resolve_target_users(db, data.user_ids, data.user_type)
        # filter by user preferences
        users = [u for u in users if u.notifications_enabled]
        count = 0
        for u in users:
            notif = Notification(user_id=u.id, title=data.title, message=data.message)
            db.add(notif)
            count += 1
        db.commit()

        # publish envelopes per user via Redis and local WS broadcast
        for u in users:
            envelope = {
                "type": "notification",
                "payload": {
                    "title": data.title,
                    "message": data.message,
                },
            }
            channel = f"{NOTIF_CHANNEL_PREFIX}{u.id}"
            await broker.start()
            await broker.publish_notification(u.id, envelope)
            await ws_manager.broadcast(channel, envelope)
        return count


notification_service = NotificationService()


