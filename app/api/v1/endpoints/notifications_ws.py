from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.websocket_manager import ws_manager
from app.services.pubsub_broker import broker
from app.services.user_service import UserService


router = APIRouter()


@router.websocket("/ws/notifications")
async def notifications_ws(
    websocket: WebSocket,
    token: str = Query(..., description="Bearer token without 'Bearer ' prefix"),
    db: Session = Depends(get_db),
):
    email = verify_token(token)
    if email is None:
        await websocket.close(code=4401)
        return
    user = UserService.get_user_by_email(db, email)
    if user is None or not user.is_active:
        await websocket.close(code=4401)
        return

    user_channel = f"notif:user:{user.id}"
    await ws_manager.connect(user_channel, websocket)

    async def on_pubsub_message(payload: dict):
        await ws_manager.broadcast(user_channel, payload)

    await broker.start()
    await broker.subscribe_user_notifications(user.id, on_pubsub_message)
    try:
        while True:
            # client doesn't send messages on this channel; keep alive via pings if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(user_channel, websocket)
    except Exception:
        ws_manager.disconnect(user_channel, websocket)
        try:
            await websocket.close()
        finally:
            pass
    finally:
        await broker.unsubscribe_user_notifications(user.id)

