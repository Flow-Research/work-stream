# Flow Platform - Technical Specification

## 1. System Architecture

### 1.1 High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                   │
│                    React + Vite (PWA)                               │
│         ┌─────────┬─────────┬─────────┬─────────┐                   │
│         │  Auth   │  Tasks  │ Worker  │  Admin  │                   │
│         │  Flow   │  Board  │  Portal │  Panel  │                   │
│         └────┬────┴────┬────┴────┬────┴────┬────┘                   │
└──────────────┼─────────┼─────────┼─────────┼────────────────────────┘
               │         │         │         │
               ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           BACKEND                                    │
│                     FastAPI (Python 3.11+)                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │   Auth   │   Task   │  Worker  │ Artifact │   Admin  │          │
│  │ Service  │ Service  │ Service  │ Service  │ Service  │          │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘          │
│       │          │          │          │          │                  │
│       ▼          ▼          ▼          ▼          ▼                  │
│  ┌──────────────────────────────────────────────────────┐           │
│  │              AI Orchestration Layer                   │           │
│  │    Claude API │ Semantic Scholar │ OpenAlex          │           │
│  └──────────────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│       PostgreSQL         │    │      Base Blockchain      │
│   - Users                │    │   - Escrow Contract       │
│   - Tasks                │    │   - Artifact Registry     │
│   - Subtasks             │    │   - cNGN Payments         │
│   - Submissions          │    │                           │
│   - Artifacts            │    │                           │
└──────────────────────────┘    └──────────────────────────┘
               │
               ▼
┌──────────────────────────┐
│          IPFS            │
│   (via Pinata)           │
│   - Artifact Storage     │
│   - File Attachments     │
└──────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Frontend | React | 18.x | Component model, ecosystem |
| Build Tool | Vite | 5.x | Fast HMR, PWA support |
| Styling | TailwindCSS | 3.x | Utility-first, responsive |
| Web3 | wagmi + viem | 2.x | Type-safe, modern |
| State | Zustand | 4.x | Simple, performant |
| Backend | FastAPI | 0.109+ | Async, OpenAPI, Python AI libs |
| ORM | SQLAlchemy | 2.0 | Async support, mature |
| Database | PostgreSQL | 15+ | JSONB, reliability |
| Migrations | Alembic | 1.13+ | Schema versioning |
| Blockchain | Base (L2) | - | Low fees, EVM compatible |
| Contracts | Solidity | 0.8.20 | Standard, auditable |
| Dev Framework | Foundry | - | Fast, Solidity tests |
| Storage | IPFS/Pinata | - | Decentralized, CDN |
| AI | Claude API | 3.5 Sonnet | Best reasoning |

---

## 2. Data Models

### 2.1 Entity Relationship Diagram

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

### 2.2 User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    wallet_address: Mapped[str] = mapped_column(String(42), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(2))
    national_id_hash: Mapped[Optional[str]] = mapped_column(String(64))
    id_verified: Mapped[bool] = mapped_column(default=False)
    id_verified_at: Mapped[Optional[datetime]] = mapped_column()
    id_verified_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    bio: Mapped[Optional[str]] = mapped_column(Text)
    reputation_score: Mapped[int] = mapped_column(default=0)
    reputation_tier: Mapped[str] = mapped_column(String(20), default="new")
    tasks_completed: Mapped[int] = mapped_column(default=0)
    tasks_approved: Mapped[int] = mapped_column(default=0)
    disputes_won: Mapped[int] = mapped_column(default=0)
    disputes_lost: Mapped[int] = mapped_column(default=0)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    banned_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
```

### 2.3 Task Model

```python
class TaskStatus(str, Enum):
    DRAFT = "draft"
    FUNDED = "funded"
    DECOMPOSED = "decomposed"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    description_html: Mapped[Optional[str]] = mapped_column(Text)
    research_question: Mapped[str] = mapped_column(Text)
    background_context: Mapped[Optional[str]] = mapped_column(Text)
    expected_outcomes: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    references: Mapped[dict] = mapped_column(JSONB, default=[])
    attachments: Mapped[dict] = mapped_column(JSONB, default=[])
    methodology_notes: Mapped[Optional[str]] = mapped_column(Text)
    client_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.DRAFT)
    total_budget_cngn: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    escrow_tx_hash: Mapped[Optional[str]] = mapped_column(String(66))
    escrow_contract_task_id: Mapped[Optional[int]] = mapped_column()
    skills_required: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    deadline: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    funded_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    client: Mapped["User"] = relationship()
    subtasks: Mapped[list["Subtask"]] = relationship(back_populates="task")
```

### 2.4 Subtask Model

```python
class SubtaskType(str, Enum):
    DISCOVERY = "discovery"
    EXTRACTION = "extraction"
    MAPPING = "mapping"
    ASSEMBLY = "assembly"
    NARRATIVE = "narrative"

class SubtaskStatus(str, Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISPUTED = "disputed"

class Subtask(Base):
    __tablename__ = "subtasks"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    description_html: Mapped[Optional[str]] = mapped_column(Text)
    subtask_type: Mapped[str] = mapped_column(String(50))
    sequence_order: Mapped[int] = mapped_column()
    budget_allocation_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    budget_cngn: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(String(20), default=SubtaskStatus.OPEN)
    claimed_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    claimed_at: Mapped[Optional[datetime]] = mapped_column()
    deliverables: Mapped[dict] = mapped_column(JSONB, default=[])
    acceptance_criteria: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    references: Mapped[dict] = mapped_column(JSONB, default=[])
    attachments: Mapped[dict] = mapped_column(JSONB, default=[])
    example_output: Mapped[Optional[str]] = mapped_column(Text)
    tools_required: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    submitted_at: Mapped[Optional[datetime]] = mapped_column()
    approved_at: Mapped[Optional[datetime]] = mapped_column()
    approved_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    auto_approved: Mapped[bool] = mapped_column(default=False)
    deadline: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    task: Mapped["Task"] = relationship(back_populates="subtasks")
    worker: Mapped[Optional["User"]] = relationship(foreign_keys=[claimed_by])
```

### 2.5 Submission Model

```python
class SubmissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Submission(Base):
    __tablename__ = "submissions"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    subtask_id: Mapped[UUID] = mapped_column(ForeignKey("subtasks.id"))
    submitted_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    content_summary: Mapped[str] = mapped_column(Text)
    artifact_ipfs_hash: Mapped[Optional[str]] = mapped_column(String(64))
    artifact_type: Mapped[Optional[str]] = mapped_column(String(50))
    artifact_on_chain_hash: Mapped[Optional[str]] = mapped_column(String(66))
    artifact_on_chain_tx: Mapped[Optional[str]] = mapped_column(String(66))
    status: Mapped[str] = mapped_column(String(20), default=SubmissionStatus.PENDING)
    review_notes: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column()
    payment_tx_hash: Mapped[Optional[str]] = mapped_column(String(66))
    payment_amount_cngn: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

### 2.6 Artifact Model

```python
class ArtifactType(str, Enum):
    DATASET = "dataset"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    REPORT = "report"

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    artifact_type: Mapped[str] = mapped_column(String(50))
    ipfs_hash: Mapped[str] = mapped_column(String(64))
    on_chain_hash: Mapped[Optional[str]] = mapped_column(String(66))
    on_chain_tx: Mapped[Optional[str]] = mapped_column(String(66))
    schema_version: Mapped[str] = mapped_column(String(20), default="1.0")
    contributors: Mapped[list[UUID]] = mapped_column(ARRAY(UUID), default=[])
    contributor_shares: Mapped[list[Decimal]] = mapped_column(ARRAY(Numeric(5, 2)), default=[])
    total_earnings_cngn: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    is_listed: Mapped[bool] = mapped_column(default=False)
    listed_price_cngn: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    royalty_cap_multiplier: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=5.0)
    royalty_expiry_years: Mapped[int] = mapped_column(default=3)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

### 2.7 Dispute Model

```python
class DisputeStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class Dispute(Base):
    __tablename__ = "disputes"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    subtask_id: Mapped[UUID] = mapped_column(ForeignKey("subtasks.id"))
    raised_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=DisputeStatus.OPEN)
    resolution: Mapped[Optional[str]] = mapped_column(Text)
    resolved_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

---

## 3. API Specification

### 3.1 Authentication Endpoints

#### GET /api/auth/nonce/{wallet_address}
Generate authentication nonce for wallet.

**Response**:
```json
{
  "nonce": "abc123def456...",
  "message": "Sign this message to authenticate with Flow: abc123def456..."
}
```

#### POST /api/auth/verify
Verify wallet signature and issue JWT.

**Request**:
```json
{
  "wallet_address": "0x1234...",
  "signature": "0xabcd...",
  "nonce": "abc123def456..."
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": { ... }
}
```

### 3.2 User Endpoints

#### GET /api/users/me
Get current authenticated user.

#### PATCH /api/users/me
Update current user profile.

**Request**:
```json
{
  "name": "New Name",
  "bio": "Updated bio",
  "skills": ["data-collection", "surveys"]
}
```

### 3.3 Task Endpoints

#### GET /api/tasks
List tasks with pagination and filters.

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `status` (string): Filter by status
- `skills` (string[]): Filter by required skills

#### POST /api/tasks
Create new task (admin only).

**Request**:
```json
{
  "title": "Research Task Title",
  "description": "Detailed description...",
  "research_question": "What is...?",
  "total_budget_cngn": "100000.00",
  "skills_required": ["research", "data-analysis"],
  "deadline": "2025-03-01T00:00:00Z"
}
```

#### POST /api/tasks/{task_id}/fund
Record task funding transaction.

**Request**:
```json
{
  "escrow_tx_hash": "0x..."
}
```

#### POST /api/tasks/{task_id}/decompose
AI-decompose task into subtasks.

**Response**:
```json
{
  "subtasks": [
    {
      "title": "Discovery Phase",
      "description": "Find relevant papers...",
      "subtask_type": "discovery",
      "budget_allocation_percent": "20.00",
      "estimated_hours": "4.00",
      "acceptance_criteria": ["At least 10 papers found", "..."]
    }
  ]
}
```

### 3.4 Subtask Endpoints

#### POST /api/subtasks/{subtask_id}/claim
Claim subtask for work.

**Request** (optional):
```json
{
  "collaborators": ["0x..."],
  "splits": ["70.00", "30.00"]
}
```

#### POST /api/subtasks/{subtask_id}/submit
Submit completed work.

**Request** (multipart/form-data):
- `content_summary`: string
- `artifact`: file (optional)
- `artifact_type`: string (json|csv|md)

#### POST /api/subtasks/{subtask_id}/approve
Approve submission (client/admin).

**Request**:
```json
{
  "submission_id": "uuid",
  "review_notes": "Good work!"
}
```

#### POST /api/subtasks/{subtask_id}/reject
Reject submission with feedback.

**Request**:
```json
{
  "submission_id": "uuid",
  "review_notes": "Please fix X, Y, Z"
}
```

### 3.5 AI Endpoints

#### POST /api/ai/papers/discover
Discover relevant papers.

**Request**:
```json
{
  "query": "machine learning healthcare Nigeria",
  "limit": 20
}
```

#### POST /api/ai/claims/extract
Extract claims from paper.

**Request**:
```json
{
  "paper_doi": "10.1234/example",
  "focus_area": "methodology"
}
```

### 3.6 Admin Endpoints

#### GET /api/admin/users
List all users (admin only).

#### POST /api/admin/users/{user_id}/verify
Mark user as verified (admin only).

#### POST /api/admin/users/{user_id}/ban
Ban user (admin only).

#### GET /api/admin/disputes
List disputes (admin only).

#### POST /api/admin/disputes/{dispute_id}/resolve
Resolve dispute (admin only).

---

## 4. Smart Contracts

### 4.1 FlowEscrow

Manages payment escrow for tasks.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract FlowEscrow is Ownable {
    IERC20 public paymentToken;
    uint256 public platformFeePercent = 10;
    address public feeRecipient;
    
    struct TaskEscrow {
        uint256 totalAmount;
        uint256 releasedAmount;
        uint256 platformFee;
        address client;
        bool completed;
        bool disputed;
    }
    
    mapping(bytes32 => TaskEscrow) public escrows;
    
    event TaskFunded(bytes32 indexed taskId, address client, uint256 amount);
    event SubtaskApproved(bytes32 indexed taskId, uint256 index, address worker, uint256 amount);
    event TaskCompleted(bytes32 indexed taskId, uint256 refundAmount);
    event DisputeRaised(bytes32 indexed taskId, address raisedBy);
    event DisputeResolved(bytes32 indexed taskId, address winner, uint256 amount);
    
    function fundTask(bytes32 taskId, uint256 amount) external;
    function approveSubtask(bytes32 taskId, uint256 subtaskIndex, address worker, uint256 amount) external onlyOwner;
    function completeTask(bytes32 taskId) external;
    function raiseDispute(bytes32 taskId) external;
    function resolveDispute(bytes32 taskId, address winner, uint256 amount) external onlyOwner;
}
```

### 4.2 FlowArtifactRegistry

On-chain artifact provenance.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract FlowArtifactRegistry is Ownable {
    struct Artifact {
        bytes32 contentHash;
        address[] contributors;
        uint256 registeredAt;
        bool exists;
    }
    
    mapping(bytes32 => Artifact) public artifacts;
    
    event ArtifactRegistered(bytes32 indexed artifactId, bytes32 contentHash, address[] contributors);
    
    function registerArtifact(bytes32 artifactId, bytes32 contentHash, address[] calldata contributors) external onlyOwner;
    function getArtifact(bytes32 artifactId) external view returns (bytes32 contentHash, address[] memory contributors, uint256 registeredAt);
    function verifyArtifact(bytes32 artifactId, bytes32 contentHash) external view returns (bool);
}
```

### 4.3 MockCNGN

Test ERC20 token for development.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockCNGN is ERC20 {
    constructor() ERC20("Mock cNGN", "mcNGN") {
        _mint(msg.sender, 1_000_000_000 * 10**18);
    }
    
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}
```

---

## 5. External Integrations

### 5.1 Claude API (AI Service)

**Purpose**: Task decomposition, claim extraction, synthesis generation.

**Configuration**:
```python
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
```

**Usage Pattern**:
```python
async def decompose_task(task: Task) -> list[SubtaskCreate]:
    response = await anthropic.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": DECOMPOSITION_PROMPT.format(
                title=task.title,
                question=task.research_question,
                context=task.background_context
            )
        }]
    )
    return parse_subtasks(response.content)
```

### 5.2 Semantic Scholar API

**Purpose**: Academic paper discovery.

**Base URL**: `https://api.semanticscholar.org/graph/v1`

**Endpoints Used**:
- `GET /paper/search` - Search papers by query
- `GET /paper/{paper_id}` - Get paper details

### 5.3 Pinata (IPFS)

**Purpose**: Artifact and file storage.

**Configuration**:
```python
PINATA_API_KEY = os.environ["PINATA_API_KEY"]
PINATA_SECRET = os.environ["PINATA_SECRET"]
PINATA_GATEWAY = "https://gateway.pinata.cloud/ipfs"
```

**Usage Pattern**:
```python
async def upload_to_ipfs(file: UploadFile) -> str:
    response = await pinata.pin_file(file)
    return response["IpfsHash"]
```

---

## 6. Directory Structure

```
Flow/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── subtasks.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── artifacts.py
│   │   │   │   └── admin.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── all_models.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── subtask.py
│   │   │   ├── submission.py
│   │   │   ├── artifact.py
│   │   │   └── dispute.py
│   │   ├── schemas/
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ai.py
│   │   │   ├── ipfs.py
│   │   │   ├── papers.py
│   │   │   └── blockchain.py
│   │   └── main.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── scripts/
│   │   └── setup_db.py
│   ├── tests/
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
├── contracts/
│   ├── src/
│   │   ├── FlowEscrow.sol
│   │   ├── FlowArtifactRegistry.sol
│   │   └── MockCNGN.sol
│   ├── test/
│   ├── script/
│   │   └── Deploy.s.sol
│   ├── foundry.toml
│   └── remappings.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── stores/
│   │   │   └── auth.ts
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── postcss.config.js
├── specs/
│   ├── brainstorm.md
│   ├── product_spec.md
│   ├── technical_spec.md
│   └── archive/
├── docker-compose.yml
├── run_dev.sh
├── run_tests.sh
├── VERSION
├── CHANGELOG.md
├── PLAN.md
├── DECISIONS.md
└── README.md
```

---

## 7. Environment Configuration

### 7.1 Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/flow

# Authentication
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Blockchain
BASE_RPC_URL=https://sepolia.base.org
ESCROW_CONTRACT_ADDRESS=0x...
REGISTRY_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...  # For backend transactions

# External APIs
CLAUDE_API_KEY=sk-ant-...
PINATA_API_KEY=...
PINATA_SECRET=...
SEMANTIC_SCHOLAR_API_KEY=...  # Optional

# Feature Flags
ENABLE_AUTO_APPROVAL=false
RATE_LIMIT_AI_REQUESTS=10
```

### 7.2 Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000/api
VITE_WALLETCONNECT_PROJECT_ID=your-project-id
VITE_CHAIN_ID=84532  # Base Sepolia
```

---

## 8. Security Considerations

### 8.1 Authentication
- Wallet signature verification using eth_sign
- JWT tokens with short expiration (24h)
- Nonce invalidation after use

### 8.2 Authorization
- Role-based access (user, admin)
- Resource ownership checks
- Rate limiting on sensitive endpoints

### 8.3 Input Validation
- Pydantic schemas for all inputs
- SQL injection prevention via ORM
- XSS prevention in HTML fields

### 8.4 Smart Contract Security
- Reentrancy guards
- Access control modifiers
- Emergency pause functionality

---

## 9. Deployment

### 9.1 Backend (Railway/Render)

```bash
# Build command
pip install -r requirements.txt

# Start command
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 9.2 Frontend (Vercel)

```bash
# Build command
npm run build

# Output directory
dist
```

### 9.3 Contracts (Base)

```bash
# Deploy to Sepolia
forge script script/Deploy.s.sol --rpc-url https://sepolia.base.org --broadcast

# Verify contracts
forge verify-contract <address> src/FlowEscrow.sol:FlowEscrow --chain base-sepolia
```

---

## 10. Testing Strategy

### 10.1 Backend Tests

```bash
# Run all tests
cd backend && pytest -v --cov=app

# Run specific module
pytest tests/test_tasks.py -v
```

### 10.2 Contract Tests

```bash
# Run Foundry tests
cd contracts && forge test -vvv

# With gas report
forge test --gas-report
```

### 10.3 Frontend Tests

```bash
# Run Vitest
cd frontend && npm test

# With coverage
npm run test:coverage
```

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*Status: Active Development*
