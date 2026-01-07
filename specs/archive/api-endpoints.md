# API Endpoints

Base URL: `http://localhost:8000/api`

## Authentication

### Get Nonce

```
GET /auth/nonce/{wallet_address}

Response:
{
  "nonce": "abc123...",
  "message": "Sign this message to authenticate with Flow: abc123..."
}
```

### Verify Signature

```
POST /auth/verify

Request:
{
  "wallet_address": "0x...",
  "signature": "0x...",
  "nonce": "abc123..."
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { ... }
}
```

## Users

### Get Current User

```
GET /users/me
Authorization: Bearer {token}

Response:
{
  "id": "uuid",
  "wallet_address": "0x...",
  "name": "John Doe",
  "country": "NG",
  "skills": ["data-collection", "surveys"],
  "reputation_score": 250,
  "reputation_tier": "active",
  ...
}
```

### Update Profile

```
PATCH /users/me
Authorization: Bearer {token}

Request:
{
  "name": "New Name",
  "bio": "Updated bio",
  "skills": ["skill1", "skill2"]
}
```

### Get User by ID

```
GET /users/{user_id}

Response:
{
  "id": "uuid",
  "name": "John Doe",
  "reputation_score": 250,
  ...
}
```

## Tasks

### List Tasks

```
GET /tasks?page=1&limit=20&status=funded

Response:
{
  "tasks": [...],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

### Get Task

```
GET /tasks/{task_id}

Response:
{
  "id": "uuid",
  "title": "Lagos Market Survey",
  "description": "...",
  "research_question": "...",
  "client_id": "uuid",
  "status": "in_progress",
  "total_budget_cngn": "150000.00",
  "skills_required": ["data-collection"],
  "deadline": "2025-02-05T00:00:00Z",
  "subtasks": [...]
}
```

### Create Task (Admin only)

```
POST /tasks
Authorization: Bearer {token}

Request:
{
  "title": "New Research Task",
  "description": "Detailed description...",
  "research_question": "What is...?",
  "total_budget_cngn": "100000.00",
  "skills_required": ["skill1", "skill2"],
  "deadline": "2025-03-01T00:00:00Z"
}

Response:
{
  "id": "uuid",
  ...
}
```

### Update Task

```
PATCH /tasks/{task_id}
Authorization: Bearer {token}

Request:
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

### Fund Task

```
POST /tasks/{task_id}/fund
Authorization: Bearer {token}

Request:
{
  "escrow_tx_hash": "0x..."
}

Response:
{
  "id": "uuid",
  "status": "funded",
  "funded_at": "2025-01-06T10:00:00Z"
}
```

### Decompose Task (AI)

```
POST /tasks/{task_id}/decompose
Authorization: Bearer {token}

Response:
{
  "subtasks": [
    {
      "title": "Discovery Phase",
      "description": "...",
      "subtask_type": "discovery",
      "budget_allocation_percent": "20.00"
    },
    ...
  ]
}
```

## Subtasks

### List Subtasks for Task

```
GET /tasks/{task_id}/subtasks

Response:
{
  "subtasks": [...],
  "total": 5
}
```

### Get Subtask

```
GET /subtasks/{subtask_id}

Response:
{
  "id": "uuid",
  "task_id": "uuid",
  "title": "Data Collection",
  "description": "...",
  "subtask_type": "extraction",
  "status": "open",
  "budget_cngn": "30000.00",
  ...
}
```

### Claim Subtask

```
POST /subtasks/{subtask_id}/claim
Authorization: Bearer {token}

Request (optional):
{
  "collaborators": ["0x..."],
  "splits": ["70.00", "30.00"]
}

Response:
{
  "id": "uuid",
  "status": "claimed",
  "claimed_by": "uuid",
  "claimed_at": "2025-01-06T10:00:00Z"
}
```

### Release Subtask

```
POST /subtasks/{subtask_id}/release
Authorization: Bearer {token}

Response:
{
  "id": "uuid",
  "status": "open",
  "claimed_by": null
}
```

### Submit Work

```
POST /subtasks/{subtask_id}/submit
Authorization: Bearer {token}
Content-Type: multipart/form-data

Fields:
- content_summary: string
- artifact: file (optional)
- artifact_type: string (json|csv|md)

Response:
{
  "submission_id": "uuid",
  "status": "pending"
}
```

### Approve Submission

```
POST /subtasks/{subtask_id}/approve
Authorization: Bearer {token}

Request:
{
  "submission_id": "uuid",
  "review_notes": "Good work!"
}

Response:
{
  "subtask_id": "uuid",
  "status": "approved"
}
```

### Reject Submission

```
POST /subtasks/{subtask_id}/reject
Authorization: Bearer {token}

Request:
{
  "submission_id": "uuid",
  "review_notes": "Please fix X, Y, Z"
}

Response:
{
  "subtask_id": "uuid",
  "status": "rejected"
}
```

## AI Services

### Discover Papers

```
POST /ai/papers/discover
Authorization: Bearer {token}

Request:
{
  "query": "machine learning healthcare Nigeria",
  "limit": 20
}

Response:
{
  "papers": [
    {
      "title": "...",
      "authors": ["..."],
      "year": 2024,
      "doi": "10.1234/...",
      "abstract": "..."
    }
  ]
}
```

### Extract Claims

```
POST /ai/claims/extract
Authorization: Bearer {token}

Request:
{
  "paper_doi": "10.1234/...",
  "focus_area": "methodology"
}

Response:
{
  "claims": [
    {
      "claim": "...",
      "evidence": "...",
      "confidence": 0.85
    }
  ]
}
```

### Synthesize

```
POST /ai/synthesize
Authorization: Bearer {token}

Request:
{
  "claims": [...],
  "format": "narrative"
}

Response:
{
  "synthesis": "..."
}
```

## Artifacts

### List Artifacts

```
GET /artifacts?listed=true&page=1&limit=20

Response:
{
  "artifacts": [...],
  "total": 10
}
```

### Get Artifact

```
GET /artifacts/{artifact_id}

Response:
{
  "id": "uuid",
  "title": "Nigeria Healthcare Dataset",
  "description": "...",
  "artifact_type": "dataset",
  "ipfs_hash": "Qm...",
  "is_listed": true,
  "listed_price_cngn": "50000.00",
  "contributors": [...],
  "contributor_shares": [...]
}
```

### Purchase Artifact

```
POST /artifacts/{artifact_id}/purchase
Authorization: Bearer {token}

Request:
{
  "payment_tx_hash": "0x..."
}

Response:
{
  "purchase_id": "uuid",
  "download_url": "https://..."
}
```

## Admin

### List Users (Admin only)

```
GET /admin/users?page=1&limit=50
Authorization: Bearer {token}

Response:
{
  "users": [...],
  "total": 100
}
```

### Verify User (Admin only)

```
POST /admin/users/{user_id}/verify
Authorization: Bearer {token}

Response:
{
  "id": "uuid",
  "id_verified": true,
  "id_verified_at": "2025-01-06T10:00:00Z"
}
```

### Ban User (Admin only)

```
POST /admin/users/{user_id}/ban
Authorization: Bearer {token}

Request:
{
  "reason": "Violation of terms"
}
```

### List Disputes (Admin only)

```
GET /admin/disputes?status=open
Authorization: Bearer {token}

Response:
{
  "disputes": [...]
}
```

### Resolve Dispute (Admin only)

```
POST /admin/disputes/{dispute_id}/resolve
Authorization: Bearer {token}

Request:
{
  "resolution": "Decided in favor of worker",
  "winner_id": "uuid"
}
```

## Error Responses

All endpoints may return:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400` - Bad request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Internal server error
