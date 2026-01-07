# Flow MVP - Build Plan

## Architecture Overview

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
│   (SQLAlchemy ORM)       │    │   - Escrow Contract       │
│   - Users                │    │   - Artifact Registry     │
│   - Tasks                │    │   - cNGN Payments         │
│   - Submissions          │    │                           │
│   - Reputation           │    │                           │
└──────────────────────────┘    └──────────────────────────┘
               │
               ▼
┌──────────────────────────┐
│          IPFS            │
│   (via Pinata)           │
│   - Artifact Storage     │
└──────────────────────────┘
```

## Component Breakdown

### Backend (FastAPI)
1. **Auth Service** - Wallet signature verification, JWT sessions
2. **User Service** - Profile management, ID verification
3. **Task Service** - Task CRUD, decomposition, funding
4. **Subtask Service** - Claims, submissions, approvals
5. **AI Service** - Claude integration, paper discovery, claim extraction
6. **Artifact Service** - IPFS storage, on-chain registration
7. **Admin Service** - User management, disputes
8. **Blockchain Service** - Contract interactions

### Frontend (React + Vite)
1. **Auth Flow** - Wallet connection, profile setup
2. **Task Board** - Browse available tasks
3. **Task Detail** - View task, subtasks, claim work
4. **Worker Dashboard** - My claims, submissions
5. **Client Dashboard** - My tasks, review submissions
6. **Admin Panel** - User verification, disputes

### Smart Contracts (Solidity + Foundry)
1. **FlowEscrow** - Payment escrow, subtask approvals
2. **FlowArtifactRegistry** - On-chain artifact hashes

## Build Order (Dependency Graph)

```
Phase 1: Foundation
├── 1.1 Backend project structure
├── 1.2 Database models & migrations
├── 1.3 Smart contracts & tests
└── 1.4 Frontend project structure

Phase 2: Core Backend
├── 2.1 Auth endpoints (depends on 1.2)
├── 2.2 User endpoints (depends on 2.1)
├── 2.3 Task endpoints (depends on 2.2)
├── 2.4 Subtask endpoints (depends on 2.3)
└── 2.5 Blockchain integration (depends on 1.3)

Phase 3: External Integrations
├── 3.1 IPFS/Pinata integration
├── 3.2 AI/Claude integration
├── 3.3 Paper APIs integration
└── 3.4 Contract event monitoring

Phase 4: Frontend
├── 4.1 Auth flow (depends on 2.1)
├── 4.2 Task pages (depends on 2.3)
├── 4.3 Worker portal (depends on 2.4)
├── 4.4 Admin panel (depends on backend)
└── 4.5 PWA setup

Phase 5: Integration & Testing
├── 5.1 End-to-end flows
├── 5.2 Contract integration tests
└── 5.3 Documentation
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| cNGN not available on Base | Medium | High | Use mock ERC20 token for testing |
| AI costs exceed budget | Low | Medium | Implement rate limits, cache queries |
| Smart contract bugs | Medium | Critical | Comprehensive tests, start small |
| Complexity creep | High | Medium | Strict scope control |
| External API rate limits | Medium | Medium | Caching, graceful degradation |

## Testing Strategy

### Unit Tests
- All service layer functions
- Database model validations
- Smart contract functions
- Component rendering

### Integration Tests
- API endpoint flows
- Contract interactions
- IPFS upload/retrieval

### E2E Tests
- Complete user journeys
- Payment flows on testnet

## Directory Structure

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
│   │   │   ├── security.py
│   │   │   └── blockchain.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── subtask.py
│   │   │   ├── submission.py
│   │   │   ├── artifact.py
│   │   │   └── dispute.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── subtask.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── subtask.py
│   │   │   ├── ai.py
│   │   │   ├── ipfs.py
│   │   │   └── blockchain.py
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── pytest.ini
├── contracts/
│   ├── src/
│   │   ├── FlowEscrow.sol
│   │   └── FlowArtifactRegistry.sol
│   ├── test/
│   │   ├── FlowEscrow.t.sol
│   │   └── FlowArtifactRegistry.t.sol
│   ├── script/
│   │   └── Deploy.s.sol
│   └── foundry.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── PLAN.md
├── DECISIONS.md
└── README.md
```

## Key Decisions (Pre-Implementation)

1. **Vite over Expo Web** - Simpler setup for web-first PWA
2. **SQLAlchemy 2.0** - Modern async support
3. **Foundry over Hardhat** - Faster compilation, better testing
4. **Mock ERC20 for MVP** - Don't depend on cNGN availability
5. **Redis optional for MVP** - Start with in-memory session cache

## Success Criteria

- [ ] User can connect wallet and create profile
- [ ] Admin can create and fund tasks
- [ ] Workers can claim, complete, and submit subtasks
- [ ] Clients can approve submissions
- [ ] Payments release via smart contract
- [ ] Artifacts stored on IPFS with on-chain hash
- [ ] Basic reputation tracking works
- [ ] Admin can manage disputes
- [ ] All tests pass
- [ ] System handles 10 concurrent users
