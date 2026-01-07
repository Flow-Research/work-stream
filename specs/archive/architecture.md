# System Architecture

## Overview

Flow is a decentralized platform connecting research clients with knowledge workers. Clients post research tasks, which are decomposed into subtasks. Workers claim subtasks, complete them using AI-assisted tools, and receive payment via blockchain escrow.

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

## Components

### Frontend (React + Vite)

| Component | Path | Description |
|-----------|------|-------------|
| Home | `/` | Landing page with platform overview |
| Tasks | `/tasks` | Browse available research tasks |
| Task Detail | `/tasks/:id` | View task details and subtasks |
| Dashboard | `/dashboard` | Worker's claimed tasks and submissions |
| Profile | `/profile` | User profile and settings |
| Admin | `/admin` | Admin panel for user management |

### Backend (FastAPI)

| Service | Routes | Description |
|---------|--------|-------------|
| Auth | `/api/auth/*` | Wallet signature verification, JWT tokens |
| Users | `/api/users/*` | Profile management, ID verification |
| Tasks | `/api/tasks/*` | Task CRUD, funding, status management |
| Subtasks | `/api/subtasks/*` | Claims, submissions, approvals |
| AI | `/api/ai/*` | Claude integration, paper discovery |
| Artifacts | `/api/artifacts/*` | IPFS storage, licensing |
| Admin | `/api/admin/*` | User management, disputes |

### Smart Contracts

| Contract | Description |
|----------|-------------|
| FlowEscrow | Payment escrow, milestone releases |
| FlowArtifactRegistry | On-chain artifact hash registration |

## Data Flow

### Task Lifecycle

```
1. Client creates task (draft)
        │
        ▼
2. Client funds escrow (funded)
        │
        ▼
3. AI decomposes into subtasks (decomposed)
        │
        ▼
4. Workers claim subtasks (in_progress)
        │
        ▼
5. Workers submit completed work (in_review)
        │
        ▼
6. Client/AI approves submissions (completed)
        │
        ▼
7. Escrow releases payments
```

### Subtask Lifecycle

```
open → claimed → in_progress → submitted → approved/rejected
                                    │
                                    └──→ disputed
```

## Directory Structure

```
Flow/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Config, security
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── scripts/             # DB setup, seeds
│   └── tests/               # pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Route pages
│   │   ├── services/        # API client
│   │   ├── stores/          # Zustand stores
│   │   └── types/           # TypeScript types
│   └── public/              # Static assets
├── contracts/
│   ├── src/                 # Solidity contracts
│   └── test/                # Foundry tests
├── specs/                   # This documentation
├── docker-compose.yml       # PostgreSQL
├── run_dev.sh              # Start all services
└── run_tests.sh            # Run all tests
```
