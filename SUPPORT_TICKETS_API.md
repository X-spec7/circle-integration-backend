## Support Tickets API

All endpoints are prefixed with the global API prefix. In this project it's `settings.api_prefix` (default `/api/v1`). Below, paths are shown relative to that prefix.

Authentication: Provide `Authorization: Bearer <token>` header for HTTP endpoints. For WebSocket, pass `?token=<token>` query.

Authorization and access control
- Admin: can manage categories, invite/remove participants, close any ticket, view any ticket and its messages.
- Non-admin: can create tickets; can view and interact only with tickets they created or were invited to (including messages and WebSocket).

### Models Overview
- TicketCategory: Admin-managed list of categories users can file tickets in.
- SupportTicket: A ticket belongs to a category and has a creator and status.
- TicketParticipant: Users allowed to chat in a given ticket; creator is added automatically. Admin can invite others.
- TicketMessage: Messages posted within a ticket (persisted and also broadcast over WebSocket).

### Categories

GET /support/categories
- Query: `active_only` (boolean, default true)
- Response: 200 OK
```json
[
  {
    "id": "uuid",
    "name": "string",
    "description": "string|null",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

POST /support/categories (Admin)
- Body:
```json
{
  "name": "string",
  "description": "string|null",
  "is_active": true
}
```
- Response: 201 Created with the created category.

PUT /support/categories/{category_id} (Admin)
- Body (all fields optional):
```json
{
  "name": "string",
  "description": "string|null",
  "is_active": true
}
```
- Response: 200 OK with updated category.

DELETE /support/categories/{category_id} (Admin)
- Response: 204 No Content

### Tickets

POST /support/tickets
- Body:
```json
{
  "category_id": "uuid",
  "title": "string"
}
```
- Rules:
  - User may have at most one OPEN ticket per category. If an OPEN ticket exists, request fails with 400.
  - If the existing ticket was CLOSED, user may create a new one.
- Response: 201 Created
```json
{
  "id": "uuid",
  "title": "string",
  "category_id": "uuid",
  "creator_id": "uuid",
  "status": "open",
  "created_at": "2025-01-01T00:00:00Z"
}
```

GET /support/tickets
- Query: `category_id` (optional)
- Response: 200 OK array of tickets the current user can see
  - Admin: sees all tickets
  - Non-admin: sees tickets they created or were invited to

GET /support/tickets/{ticket_id}
- Permissions: creator, participant, or admin
- Response: 200 OK ticket details (same shape as creation response)

POST /support/tickets/{ticket_id}/close
- Permissions: Admin or the ticket creator
- Response: 200 OK ticket with `status` set to `closed`

<!-- Unread tracking removed -->

### Participants

POST /support/tickets/{ticket_id}/participants (Admin)
- Body:
```json
{
  "user_id": "uuid"
}
```
- Response: 201 Created
```json
{
  "id": "uuid",
  "ticket_id": "uuid",
  "user_id": "uuid",
  "is_admin_invited": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

DELETE /support/tickets/{ticket_id}/participants/{user_id} (Admin)
- Removes a participant from the ticket (cannot remove the ticket creator)
- Response: 204 No Content

### Messages (HTTP)

POST /support/tickets/{ticket_id}/messages
- Body:
```json
{
  "content": "string"
}
```
- Permissions: creator, participant, or admin (ticket must be open)
- Response: 201 Created
```json
{
  "id": "uuid",
  "ticket_id": "uuid",
  "sender_id": "uuid",
  "sender_name": "string",
  "content": "string",
  "created_at": "2025-01-01T00:00:00Z"
}
```

GET /support/tickets/{ticket_id}/messages?page=1&limit=50
- Permissions: creator, participant, or admin
- Response: 200 OK
```json
{
  "items": [
    {
      "id": "uuid",
      "ticket_id": "uuid",
      "sender_id": "uuid",
      "sender_name": "string",
      "content": "string",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
PUT /support/tickets/{ticket_id}/messages/{message_id}
- Body:
```json
{
  "content": "string"
}
```
- Permissions: author of the message or admin
- Response: 200 OK (same shape as message create response)

DELETE /support/tickets/{ticket_id}/messages/{message_id}
- Permissions: author of the message or admin
- Response: 204 No Content
  "total": 1,
  "page": 1,
  "limit": 50,
  "total_pages": 1
}
```

### Real-time Chat (WebSocket)

Path: /api/v1/ws/tickets/{ticket_id}?token=<JWT>
- On connect: server verifies token and that user is allowed for the ticket (creator, participant, or admin). If unauthorized, connection is closed.
- Client-to-server message format:
```json
{ "content": "string" }
```
- Server broadcasts to all connected clients on that ticket room:
```json
{
  "type": "ticket.message",
  "payload": {
    "id": "uuid",
    "ticket_id": "uuid",
    "sender_id": "uuid",
    "sender_name": "string",
    "content": "string",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

Notes:
- Messages sent over WebSocket are persisted first, then broadcast.
- If a ticket is closed, sending messages will fail.
 - Scalable fanout: WebSocket messages are broadcast locally and via Redis pub/sub (`REDIS_URL`). Multiple app instances will receive and forward messages to their connected clients. Other services (e.g., notifications) may subscribe to the same Redis channels (`ticket:<ticket_id>:message`).


