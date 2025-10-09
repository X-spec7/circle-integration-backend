from typing import Dict, Set
from fastapi import WebSocket


class WebSocketConnectionManager:
    """In-memory manager mapping ticket rooms to websocket connections"""

    def __init__(self) -> None:
        self.ticket_id_to_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, ticket_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.ticket_id_to_connections.setdefault(ticket_id, set()).add(websocket)

    def disconnect(self, ticket_id: str, websocket: WebSocket) -> None:
        conns = self.ticket_id_to_connections.get(ticket_id)
        if not conns:
            return
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            del self.ticket_id_to_connections[ticket_id]

    async def broadcast(self, ticket_id: str, message: dict) -> None:
        conns = self.ticket_id_to_connections.get(ticket_id, set())
        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                # Best-effort cleanup
                self.disconnect(ticket_id, ws)


ws_manager = WebSocketConnectionManager()


