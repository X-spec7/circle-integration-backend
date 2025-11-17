## WebSockets in This Backend

This backend exposes WebSocket (WS) services alongside HTTP APIs. WS endpoints are grouped under `app/api/v1/ws/` to clearly distinguish them from HTTP routes in `app/api/v1/endpoints/`.

### Overview
- Package for WS routes: `app/api/v1/ws/`
  - `support_ws.py` — live chat for support tickets: `/api/v1/ws/tickets/{ticket_id}`
  - `notifications_ws.py` — user notifications stream: `/api/v1/ws/notifications`
- Shared WS infra:
  - `app/services/ws/websocket_manager.py` — in-memory connection manager (room → active sockets)
  - `app/services/ws/pubsub_broker.py` — Redis pub/sub broker for cross-instance fanout

### Routing and Mounting
Routers are included in `app/api/v1/api.py`:
```python
from app.api.v1.ws import support_ws, notifications_ws
api_router.include_router(support_ws.router, tags=["Support WebSocket"])
api_router.include_router(notifications_ws.router, tags=["Notifications WebSocket"])
```

### Authentication
Both WS endpoints authenticate with a JWT passed as a query parameter `token`:
- Example client URL: `/api/v1/ws/notifications?token=<JWT>`
- On connect, the server validates the token via `app.core.security.verify_token`.
- If invalid or user inactive, the server closes with code `4401` (Unauthorized).

Why query param? Many WS clients cannot reliably set Authorization headers during the HTTP→WS upgrade. Passing the token in the query string is a pragmatic approach; ensure you use WSS and short-lived tokens.

### Support Ticket Chat (`/ws/tickets/{ticket_id}`)
- Auth: required, via `token` query param.
- Authorization: user must be a participant in the ticket; otherwise the connection is closed with `4403` (Forbidden).
- Client → Server:
  - JSON messages `{ "content": "..." }`
- Server behavior:
  - Persists messages via `support_service.add_message(...)`
  - Broadcasts to all sockets in the ticket room using `websocket_manager`
  - Publishes the message to Redis so other app instances fan out the message too

### Notifications Stream (`/ws/notifications`)
- Auth: required, via `token` query param.
- Rooming: user joins their own channel `notif:user:{user_id}`.
- Server → Client:
  - Arbitrary event envelopes, e.g.:
    ```json
    {
      "type": "notification",
      "payload": { "title": "string", "message": "string" }
    }
    ```
- No client messages are expected; the server keeps the socket open (optionally with pings).

### Connection Management
`app/services/websocket_manager.py`
- Accepts sockets and tracks them by room key.
- `connect(room, ws)` — accepts and registers.
- `disconnect(room, ws)` — removes a socket; cleans up empty rooms.
- `broadcast(room, message)` — sends JSON to all sockets in room; drops broken sockets on error.

This manager is intentionally simple and in-memory. It is combined with Redis pub/sub to scale horizontally.

### Cross-Instance Fanout with Redis
`app/services/pubsub_broker.py`
- Uses `settings.redis_url` to connect to Redis.
- Channels:
  - `ticket:{ticket_id}:message` — support chat messages
  - `notif:user:{user_id}` — personal notifications
- Methods:
  - `publish_ticket_message(ticket_id, message)`
  - `subscribe_ticket(ticket_id, on_message)`
  - `publish_notification(user_id, message)`
  - `subscribe_user_notifications(user_id, on_message)`
- The broker runs an async listener task that dispatches payloads to registered callbacks.

### Lifecycle and Error Codes
- Accept: sockets are accepted on connect if auth succeeds.
- Close codes:
  - `4401` — Unauthorized (bad/missing token, inactive user)
  - `4403` — Forbidden (not allowed to join ticket)
- Disconnect handling:
  - Broken sockets are removed from in-memory sets.
  - Subscriptions are cleaned up with `unsubscribe_*` in `finally` blocks.

### Client Examples
JavaScript (Notifications):
```js
const token = "<JWT>";
const ws = new WebSocket(`wss://your.domain/api/v1/ws/notifications?token=${encodeURIComponent(token)}`);
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  console.log("notification:", msg);
};
ws.onclose = (ev) => console.log("closed:", ev.code, ev.reason);
```

JavaScript (Support Ticket Chat):
```js
const token = "<JWT>";
const ticketId = "<ticket-uuid>";
const ws = new WebSocket(`wss://your.domain/api/v1/ws/tickets/${ticketId}?token=${encodeURIComponent(token)}`);
ws.onmessage = (ev) => console.log("chat:", JSON.parse(ev.data));
ws.onopen = () => ws.send(JSON.stringify({ content: "Hello support!" }));
```

### Operational Notes
- Ensure Redis is reachable (`REDIS_URL`).
- Prefer WSS in production.
- JWTs should be short-lived; rotate frequently.
- Horizontal scaling: any number of app instances can serve sockets; Redis ensures broadcast fanout across instances.

### Directory Layout
```
app/
  api/
    v1/
      endpoints/        # HTTP endpoints (REST)
      ws/               # WebSocket endpoints (WS)
  services/
    ws/
      websocket_manager.py
      pubsub_broker.py
```


