## KYC (ComplyCube) API

- Base path: `/api/v1`
- Auth: All `/kyc/*` endpoints require `Authorization: Bearer <token>`
- Content-Type: `application/json` unless noted
- Enum: `KycStatus` = `not_started | review | verified | declined`

### Create KYC Client
- Method/Path: POST `/kyc/create-client`
- Auth: Required
- Request
```json
{
  "client_type": "person",
  "entity_name": "John Doe",
  "email": "john@example.com"
}
```
- Response 200 (KycClientOut)
```json
{
  "id": "string-uuid",
  "complycube_client_id": "cc_client_id",
  "user_id": "string-uuid",
  "client_type": "person",
  "entity_name": "John Doe",
  "email": "john@example.com",
  "status": "not_started",
  "status_text": null
}
```

### Create Verification Session
- Method/Path: POST `/kyc/create-session/{complycube_client_id}`
- Auth: Required
- Path params
  - `complycube_client_id`: string
- Request
```json
{
  "session_type": "document_check",
  "redirect_url": "https://yourapp.com/kyc/callback",
  "webhook_url": "https://your.domain/api/v1/webhooks/complycube"
}
```
- Response 200
```json
{
  "id": "cc_session_id",
  "session_url": "https://.../start-session"
}
```

### Get KYC Status (current user)
- Method/Path: GET `/kyc/status`
- Auth: Required
- Response 200 (exists)
```json
{
  "success": true,
  "complycube_client_id": "cc_client_id",
  "status": "review",
  "status_text": "Waiting for review",
  "created_at": "2025-10-19T17:35:00+00:00",
  "updated_at": "2025-10-19T17:40:00+00:00"
}
```
- Response 200 (none)
```json
{ "success": false, "message": "No KYC record found" }
```

### Download KYC Document
- Method/Path: GET `/kyc/download-document/{document_id}`
- Auth: Required
- Path params
  - `document_id`: string
- Query params
  - `side`: `front` | `back` (default `front`)
- Response 200: Binary file stream with `Content-Type` from ComplyCube and `Content-Disposition: attachment; filename=<name>`
- Response 404
```json
{ "detail": "Document not found" }
```

### Manual Review (admin)
- Method/Path: POST `/kyc/manual-review/{complycube_client_id}`
- Auth: Required (admin)
- Path params
  - `complycube_client_id`: string
- Query params
  - `action`: `approve` | `reject`
- Response 200
```json
{ "success": true }
```

### Webhook (ComplyCube)
- Method/Path: POST `/webhooks/complycube`
- Auth: None (secured by signature)
- Headers
  - `X-Signature`: HMAC-SHA256 of raw body using `COMPLYCUBE_WEBHOOK_SECRET`
- Handled events
  - `verification.completed` (fields used: `type`, `clientId`, `status`, `statusText`)
- Response 200
```json
{ "success": true }
```
- Response 401 (bad signature)
```json
{ "detail": "invalid signature" }
```

### Schemas
- KycClientCreate
```json
{ "client_type": "person|company", "entity_name": "string", "email": "email" }
```

- KycClientOut
```json
{
  "id": "string-uuid",
  "complycube_client_id": "string",
  "user_id": "string-uuid",
  "client_type": "person|company",
  "entity_name": "string|null",
  "email": "email|null",
  "status": "not_started|review|verified|declined",
  "status_text": "string|null"
}
```

- KycSessionCreate
```json
{
  "session_type": "document_check",
  "redirect_url": "string-url",
  "webhook_url": "string-url"
}
```

- KycSessionOut
```json
{ "id": "string", "session_url": "string|null" }
```


