# Data Models

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │    Task     │       │   Subtask   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────│ client_id   │       │ id (PK)     │
│ wallet_addr │       │ id (PK)     │◄──────│ task_id     │
│ name        │       │ title       │       │ claimed_by  │──►User
│ country     │       │ description │       │ approved_by │──►User
│ skills[]    │       │ status      │       │ title       │
│ reputation  │       │ budget      │       │ description │
│ is_admin    │       │ deadline    │       │ status      │
└─────────────┘       └─────────────┘       │ budget      │
      │                                      └─────────────┘
      │                                            │
      │       ┌─────────────┐                      │
      │       │ Submission  │                      │
      │       ├─────────────┤                      │
      └──────►│ submitted_by│◄─────────────────────┘
              │ subtask_id  │
              │ status      │
              │ ipfs_hash   │
              └─────────────┘
                    │
                    ▼
              ┌─────────────┐       ┌─────────────────┐
              │  Artifact   │       │ ArtifactPurchase│
              ├─────────────┤       ├─────────────────┤
              │ id (PK)     │◄──────│ artifact_id     │
              │ task_id     │       │ buyer_id        │──►User
              │ ipfs_hash   │       │ amount          │
              │ contributors│       │ tx_hash         │
              └─────────────┘       └─────────────────┘
```

## Models

### User

Platform participants: workers, clients, and admins.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| wallet_address | String(42) | Ethereum address, unique |
| name | String(255) | Display name |
| country | String(2) | ISO country code |
| national_id_hash | String(64) | Hashed national ID for verification |
| id_verified | Boolean | KYC verification status |
| id_verified_at | DateTime | When verified |
| id_verified_by | UUID | Admin who verified |
| skills | Text[] | Array of skill tags |
| bio | Text | Profile description |
| reputation_score | Integer | Accumulated reputation points |
| reputation_tier | String(20) | new, active, established, expert |
| tasks_completed | Integer | Count of completed tasks |
| tasks_approved | Integer | Count of approved submissions |
| disputes_won | Integer | Disputes decided in user's favor |
| disputes_lost | Integer | Disputes lost |
| is_admin | Boolean | Admin privileges |
| is_banned | Boolean | Account banned |
| banned_reason | Text | Reason for ban |
| created_at | DateTime | Account creation |
| updated_at | DateTime | Last update |

### Task

Research projects posted by clients.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | String(500) | Task title |
| description | Text | Detailed description |
| research_question | Text | Core research question |
| client_id | UUID | FK to User |
| status | String(20) | draft, funded, decomposed, in_progress, in_review, completed, cancelled, disputed |
| total_budget_cngn | Decimal(18,2) | Total budget in cNGN |
| escrow_tx_hash | String(66) | Funding transaction hash |
| escrow_contract_task_id | Integer | On-chain task ID |
| skills_required | Text[] | Required skill tags |
| deadline | DateTime | Task deadline |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update |
| funded_at | DateTime | When funded |
| completed_at | DateTime | When completed |

### Subtask

Decomposed units of work within a task.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| task_id | UUID | FK to Task |
| title | String(500) | Subtask title |
| description | Text | Work requirements |
| subtask_type | String(50) | discovery, extraction, mapping, assembly, narrative |
| sequence_order | Integer | Execution order |
| budget_allocation_percent | Decimal(5,2) | Percentage of task budget |
| budget_cngn | Decimal(18,2) | Absolute budget amount |
| status | String(20) | open, claimed, in_progress, submitted, approved, rejected, disputed |
| claimed_by | UUID | FK to User (worker) |
| claimed_at | DateTime | When claimed |
| collaborators | UUID[] | Additional workers |
| collaborator_splits | Decimal[] | Payment splits |
| submitted_at | DateTime | When submitted |
| approved_at | DateTime | When approved |
| approved_by | UUID | FK to User (reviewer) |
| auto_approved | Boolean | AI auto-approval flag |
| deadline | DateTime | Subtask deadline |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update |

### Submission

Work submitted by workers for subtasks.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| subtask_id | UUID | FK to Subtask |
| submitted_by | UUID | FK to User |
| content_summary | Text | Summary of work |
| artifact_ipfs_hash | String(64) | IPFS CID of artifact |
| artifact_type | String(50) | json, csv, md |
| artifact_on_chain_hash | String(66) | On-chain hash |
| artifact_on_chain_tx | String(66) | Registration tx hash |
| status | String(20) | pending, approved, rejected |
| review_notes | Text | Reviewer feedback |
| reviewed_by | UUID | FK to User |
| reviewed_at | DateTime | Review timestamp |
| payment_tx_hash | String(66) | Payment transaction |
| payment_amount_cngn | Decimal(18,2) | Payment amount |
| created_at | DateTime | Submission timestamp |

### Artifact

Reusable outputs available for licensing.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| task_id | UUID | FK to Task |
| title | String(500) | Artifact title |
| description | Text | Artifact description |
| artifact_type | String(50) | dataset, knowledge_graph |
| ipfs_hash | String(64) | IPFS CID |
| on_chain_hash | String(66) | On-chain hash |
| on_chain_tx | String(66) | Registration tx |
| schema_version | String(20) | Data schema version |
| contributors | UUID[] | Contributing workers |
| contributor_shares | Decimal[] | Revenue shares |
| total_earnings_cngn | Decimal(18,2) | Total royalties earned |
| is_listed | Boolean | Available for purchase |
| listed_price_cngn | Decimal(18,2) | Purchase price |
| royalty_cap_multiplier | Decimal(3,1) | Max royalty (5x default) |
| royalty_expiry_years | Integer | Royalty term (3 years default) |
| created_at | DateTime | Creation timestamp |

### Dispute

Conflict resolution records.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| subtask_id | UUID | FK to Subtask |
| raised_by | UUID | FK to User |
| reason | Text | Dispute reason |
| status | String(20) | open, resolved, escalated |
| resolution | Text | Resolution details |
| resolved_by | UUID | FK to User (admin) |
| resolved_at | DateTime | Resolution timestamp |
| created_at | DateTime | When raised |

## Indexes

| Table | Columns | Type |
|-------|---------|------|
| users | wallet_address | UNIQUE |
| tasks | status | INDEX |
| tasks | client_id | INDEX |
| subtasks | task_id | INDEX |
| subtasks | status | INDEX |
| subtasks | claimed_by | INDEX |
| submissions | subtask_id | INDEX |
