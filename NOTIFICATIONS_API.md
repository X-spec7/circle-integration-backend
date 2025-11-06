## Notifications API

All paths are relative to `settings.api_prefix` (default `/api/v1`). Auth via `Authorization: Bearer <token>`.

### WebSocket

Path: `/api/v1/ws/notifications?token=<JWT>`
- On connect, user is authenticated and joined to their user-specific room.
- Server → client envelope:
```json
{
  "type": "notification",
  "payload": {
    "title": "string",
    "message": "string"
  }
}
```

### Admin Send Notifications

POST `/notifications/send` (Admin)
- Body:
```json
{
  "title": "string",
  "message": "string",
  "user_ids": ["uuid"],
  "user_type": "sme" | "investor" | "admin"
}
```
- Behavior: targets `user_ids` if provided; otherwise all users of `user_type`. Only users with notifications enabled receive.
- Response 202:
```json
{ "sent": 123 }
```

### User Notification Settings

PUT `/notifications/settings`
- Body:
```json
{ "notifications_enabled": true }
```
- Response 200:
```json
{ "notifications_enabled": true }
```


