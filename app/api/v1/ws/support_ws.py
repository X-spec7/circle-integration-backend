from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.ws.websocket_manager import ws_manager
from app.services.support_service import support_service
from app.services.user_service import UserService
from app.services.ws.pubsub_broker import broker


router = APIRouter()


@router.websocket("/ws/tickets/{ticket_id}")
async def ticket_chat_ws(
    websocket: WebSocket,
    ticket_id: str,
    token: str = Query(..., description="Bearer token without 'Bearer ' prefix"),
    db: Session = Depends(get_db),
):
    # Authenticate
    email = verify_token(token)
    if email is None:
        await websocket.close(code=4401)
        return
    
    user = UserService.get_user_by_email(db, email)
    if user is None or not user.is_active:
        await websocket.close(code=4401)
        return

    # Authorize participation
    try:
        support_service.get_ticket(db, ticket_id, user)
    except Exception:
        await websocket.close(code=4403)
        return

    await ws_manager.connect(ticket_id, websocket)
    # subscribe to Redis channel so this instance receives messages from other instances
    async def on_pubsub_message(payload: dict):
        await ws_manager.broadcast(ticket_id, payload)

    await broker.start()
    await broker.subscribe_ticket(ticket_id, on_pubsub_message)
    
    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue
            # Persist message and broadcast
            msg = support_service.add_message(db, ticket_id, user, type("obj", (), {"content": content}))
            envelope = {
                "type": "ticket.message",
                "payload": {
                    "id": msg.id,
                    "ticket_id": ticket_id,
                    "sender_id": user.id,
                    "sender_name": user.name,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                },
            }
            # local broadcast and publish to Redis for cross-instance fanout
            await ws_manager.broadcast(ticket_id, envelope)
            await broker.publish_ticket_message(ticket_id, envelope)
    except WebSocketDisconnect:
        ws_manager.disconnect(ticket_id, websocket)
    except Exception:
        ws_manager.disconnect(ticket_id, websocket)
        try:
            await websocket.close()
        finally:
            pass
    finally:
        await broker.unsubscribe_ticket(ticket_id)


