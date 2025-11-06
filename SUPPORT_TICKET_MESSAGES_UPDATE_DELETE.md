## Ticket Messages - Update and Delete

Authentication: `Authorization: Bearer <token>`

Base prefix: `settings.api_prefix` (default `/api/v1`)

### Update Message

PUT /support/tickets/{ticket_id}/messages/{message_id}

Path params:
- `ticket_id`: string (uuid)
- `message_id`: string (uuid)

Request body (application/json):
```json
{
  "content": "string"
}
```

Response 200 (application/json):
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

Notes:
- Only the author of the message or an admin can update.

### Delete Message

DELETE /support/tickets/{ticket_id}/messages/{message_id}

Path params:
- `ticket_id`: string (uuid)
- `message_id`: string (uuid)

Response 204 No Content

Notes:
- Only the author of the message or an admin can delete.


