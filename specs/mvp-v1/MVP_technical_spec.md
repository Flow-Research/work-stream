# Flow Platform — MVP Technical Specification

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Approved  
**Target MVP Date:** Q1 2025  
**Full Spec Reference:** technical_spec.md

---

## 1. MVP Overview

### 1.1 MVP Goal

Validate that knowledge workers can successfully complete research subtasks, submit work with file uploads, and receive payment through blockchain escrow — demonstrating the core value loop of the Flow platform.

### 1.2 Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| End-to-end task completion | 5 tasks | Count tasks reaching "completed" status |
| Worker submissions | 25 submissions | Count submissions with IPFS artifacts |
| Payment releases | 20 payments | Count successful escrow releases |
| First-submission approval rate | >70% | Approved / Total submissions |
| Platform uptime | 95% | Health check monitoring |

### 1.3 MVP Scope Summary

#### In Scope (MVP)

- Wallet-based authentication with profile creation
- Task creation and AI decomposition (admin)
- Subtask claiming by workers
- **Work submission with IPFS file upload**
- **Submission review (approve/reject)**
- **Smart contract escrow deployment**
- **Payment release on approval**
- Basic admin panel (user list, disputes view)
- Worker dashboard with claimed tasks

#### Explicitly Out of Scope (Post-MVP)

| Item | Reason Deferred | When to Add |
|------|-----------------|-------------|
| ID Verification (KYC) | Not blocking core flow | After 50+ users |
| Artifact marketplace | Requires completed tasks first | MVP+1 |
| Artifact licensing/royalties | Complex payment splits | MVP+2 |
| Auto-approval (AI review) | Need manual baseline first | After 100 submissions |
| PWA offline mode | Not critical for validation | MVP+1 |
| Advanced analytics | Need data first | MVP+1 |
| Real-time notifications | Polling sufficient | MVP+1 |

### 1.4 MVP vs Full Spec Comparison

| Area | Full Spec | MVP Scope | Delta |
|------|-----------|-----------|-------|
| Features | 18 features | 12 features | 6 deferred |
| User types | Worker, Client, Admin | Worker, Admin | Client = Admin for MVP |
| Integrations | 4 (Claude, IPFS, Blockchain, Papers) | 4 (all needed) | None |
| Scale target | 100 concurrent | 20 concurrent | Growth path defined |

---

## 2. MVP Architecture

### 2.1 Architecture Overview

Same as full spec — no architectural simplifications. All MVP code is production-ready.

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                   │
│                    React + Vite + TailwindCSS                       │
│         ┌─────────┬─────────┬─────────┬─────────┐                   │
│         │  Auth   │  Tasks  │ Worker  │  Admin  │                   │
│         │  Flow   │  Board  │  Portal │  Panel  │                   │
│         └────┬────┴────┬────┴────┬────┴────┬────┘                   │
└──────────────┼─────────┼─────────┼─────────┼────────────────────────┘
               │         │         │         │
               ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                          │
│  Auth │ Users │ Tasks │ Subtasks │ AI │ Artifacts │ Admin           │
└──────────────────────────────────────────────────────────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│       PostgreSQL         │    │      Base Sepolia         │
│   All models deployed    │    │   FlowEscrow + Registry   │
└──────────────────────────┘    └──────────────────────────┘
               │
               ▼
┌──────────────────────────┐
│     IPFS (Pinata)        │
│   Artifact Storage       │
└──────────────────────────┘
```

### 2.2 Architecture Decisions (MVP-Specific)

#### ADR-MVP-001: Single Admin Role for MVP

- **Context:** Full spec separates Client and Admin roles
- **Decision:** For MVP, admin creates and manages tasks (acting as client)
- **Full spec approach:** Separate client role with own dashboard
- **Migration path:** Add client role and permissions post-MVP

#### ADR-MVP-002: Manual Contract Interaction via Backend

- **Context:** Full spec has event-driven updates
- **Decision:** Backend calls contract on approval, no event listeners
- **Full spec approach:** Event monitoring service
- **Migration path:** Add event listener service post-MVP

### 2.3 MVP Component Architecture

#### Component: Frontend

- **MVP Scope:** All 6 pages functional with core interactions
- **Simplified behaviors:** No real-time updates (manual refresh)
- **Full spec delta:** WebSocket notifications, PWA offline
- **Technology:** React 18, Vite, TailwindCSS, wagmi, Zustand

#### Component: Backend

- **MVP Scope:** All endpoints implemented
- **Simplified behaviors:** Sync contract calls (no event queue)
- **Full spec delta:** Event monitoring, caching, rate limiting
- **Technology:** FastAPI, SQLAlchemy 2.0, asyncpg

#### Component: Smart Contracts

- **MVP Scope:** FlowEscrow + FlowArtifactRegistry deployed
- **Simplified behaviors:** Admin-only contract calls
- **Full spec delta:** Multi-sig, timelocks, pausability
- **Technology:** Solidity 0.8.20, Foundry, Base Sepolia

### 2.4 Deferred Architecture Elements

| Element | Full Spec Purpose | Why Deferred | Pre-requisite For |
|---------|-------------------|--------------|-------------------|
| Event Listener | Real-time status updates | Complexity, polling works | Real-time UX |
| Redis Cache | Session/query caching | In-memory sufficient | Scale beyond 50 users |
| WebSocket | Live notifications | Not critical path | Real-time features |

---

## 3. MVP Data Architecture

### 3.1 MVP Data Models

All models from technical_spec.md are included. No schema simplifications — build for full spec from day one.

#### Entity: User
- **MVP fields:** All fields implemented
- **Deferred fields:** None
- **Migration note:** Schema complete

#### Entity: Task
- **MVP fields:** All fields implemented
- **Deferred fields:** None
- **Migration note:** Schema complete

#### Entity: Subtask
- **MVP fields:** All fields implemented
- **Deferred fields:** None
- **Migration note:** Schema complete

#### Entity: Submission
- **MVP fields:** All fields implemented
- **Deferred fields:** None
- **Migration note:** Schema complete

#### Entity: Artifact
- **MVP fields:** All fields implemented
- **Deferred fields:** licensing fields unused until marketplace
- **Migration note:** Schema complete, features deferred

#### Entity: Dispute
- **MVP fields:** All fields implemented
- **Deferred fields:** None
- **Migration note:** Schema complete

### 3.2 MVP Database Design

- **Database:** PostgreSQL 15+
- **MVP tables:** All 6 tables (users, tasks, subtasks, submissions, artifacts, disputes)
- **Deferred tables:** None

### 3.3 MVP Data Constraints

| Constraint | MVP Approach | Full Spec Approach | Migration |
|------------|--------------|-------------------|-----------|
| Max claims per worker | 3 (enforced in code) | Configurable per tier | Add config table |
| Claim expiry | 48 hours (hardcoded) | Configurable | Add to settings |

---

## 4. MVP API Specification

### 4.1 MVP API Surface

| Endpoint | MVP | Post-MVP | Notes |
|----------|-----|----------|-------|
| POST /auth/nonce | ✓ | — | Implemented |
| POST /auth/verify | ✓ | — | Implemented |
| GET /users/me | ✓ | — | Implemented |
| PATCH /users/me | ✓ | — | Implemented |
| GET /tasks | ✓ | — | Implemented |
| POST /tasks | ✓ | — | Implemented |
| POST /tasks/{id}/fund | ✓ | Enhanced | Wire to contract |
| POST /tasks/{id}/decompose | ✓ | — | Implemented |
| POST /subtasks/{id}/claim | ✓ | — | Implemented |
| POST /subtasks/{id}/submit | ✓ | — | **Needs IPFS integration** |
| POST /subtasks/{id}/approve | ✓ | — | **Needs contract call** |
| POST /subtasks/{id}/reject | ✓ | — | Implemented |
| GET /admin/users | ✓ | Enhanced | Implemented |
| GET /admin/disputes | ✓ | Enhanced | Implemented |

### 4.2 MVP Endpoint Specifications

#### POST /api/subtasks/{subtask_id}/submit

- **MVP Scope:** Upload artifact to IPFS, create submission record
- **Simplified behaviors:**
  - Single file upload only
  - Max 10MB file size
- **Current status:** Endpoint exists, IPFS upload is TODO
- **Post-MVP additions:**
  - Multiple file uploads
  - Larger file support
  - Progress indicators

#### POST /api/subtasks/{subtask_id}/approve

- **MVP Scope:** Approve submission, trigger payment via contract
- **Simplified behaviors:**
  - Synchronous contract call
  - Manual retry on failure
- **Current status:** Endpoint exists, contract call not wired
- **Post-MVP additions:**
  - Event-driven confirmation
  - Automatic retry queue

### 4.3 MVP Error Handling

- **Approach:** Consistent error response format, basic retry logic
- **Deferred:** Structured error codes, automatic retry queues

---

## 5. MVP Security

### 5.1 MVP Security Scope

| Security Control | MVP Implementation | Full Spec | Notes |
|-----------------|-------------------|-----------|-------|
| Authentication | Wallet signature + JWT | Same | Complete |
| Authorization | Role check (user/admin) | Same | Complete |
| Input validation | Pydantic schemas | Same | Complete |
| Rate limiting | Basic (10 req/min AI) | Tiered | Simplified |

### 5.2 MVP Authentication

Fully implemented — no shortcuts on auth security.

### 5.3 MVP Authorization

Two roles: user and admin. Admin = is_admin flag on user.

### 5.4 Security Items Deferred

| Item | Risk of Deferring | Mitigation | Add By |
|------|-------------------|------------|--------|
| Advanced rate limiting | Low (small user base) | Basic limits in place | 100+ users |
| Audit logging | Low | Manual log review | MVP+1 |

---

## 6. MVP Infrastructure

### 6.1 MVP Infrastructure Architecture

| Component | MVP Setup | Full Spec Setup | Scale Trigger |
|-----------|-----------|-----------------|---------------|
| Backend | Single Railway instance | Multi-instance + LB | 50+ concurrent |
| Database | Managed PostgreSQL | Same + read replicas | 10k+ rows/table |
| Frontend | Vercel | Same | N/A |
| Contracts | Base Sepolia | Base Mainnet | Production launch |

### 6.2 MVP Deployment

- **Environments:** Local + Staging (Sepolia)
- **Deployment approach:** Git push to deploy
- **Rollback:** Git revert + redeploy

### 6.3 MVP CI/CD Pipeline

```
Push to main → Run tests → Build → Deploy to staging
```

### 6.4 Infrastructure Deferred

| Item | Why Deferred | Trigger to Add |
|------|--------------|----------------|
| Production env | Need testnet validation | After beta success |
| Monitoring (Datadog) | Cost | 50+ users |
| CDN | Low traffic | Performance issues |

---

## 7. MVP Monitoring & Operations

### 7.1 MVP Observability

| Category | MVP Coverage | Full Spec Coverage |
|----------|--------------|-------------------|
| Metrics | Health endpoint + manual | Prometheus + Grafana |
| Logging | Console + stdout | Structured JSON + aggregation |
| Alerting | Manual monitoring | PagerDuty |

### 7.2 MVP Alerts

| Alert | Condition | Response |
|-------|-----------|----------|
| API down | Health check fails | Manual restart |
| Contract failure | Transaction reverts | Manual investigation |

### 7.3 MVP Operational Procedures

- **On-call:** Developer monitoring during beta
- **Incident response:** Slack channel + manual triage
- **Runbooks needed:** Contract deployment, database backup

---

## 8. MVP Integrations

### 8.1 MVP Integration Scope

| Integration | MVP | Post-MVP | Rationale |
|-------------|-----|----------|-----------|
| Claude API | ✓ | — | Required for decomposition |
| Pinata (IPFS) | ✓ | — | Required for submissions |
| Base blockchain | ✓ | — | Required for payments |
| Semantic Scholar | ✓ | — | Paper discovery works |

### 8.2 MVP Integration Specifications

#### Integration: Pinata (IPFS)

- **MVP Usage:** Upload submission artifacts, store with hash
- **Simplified approach:** Direct upload, no chunking
- **Error handling:** Retry 3x, fail with error message
- **Fallback:** Store locally with warning (dev only)

#### Integration: Base Sepolia (Blockchain)

- **MVP Usage:** Fund tasks, approve subtasks, release payments
- **Simplified approach:** Backend wallet signs transactions
- **Error handling:** Retry with exponential backoff
- **Fallback:** Manual admin intervention

---

## 9. MVP Technical Constraints & Assumptions

### 9.1 MVP Constraints

| Constraint | Impact | Workaround |
|------------|--------|------------|
| Single admin wallet | All contract calls from one key | Secure key management |
| Testnet only | No real value at stake | Clear testnet labeling |
| MockCNGN token | Not real currency | Faucet for test tokens |

### 9.2 MVP Assumptions

| Assumption | If Wrong | Validation Method |
|------------|----------|-------------------|
| 20 concurrent users sufficient | Add caching/scaling | Monitor response times |
| Workers have MetaMask | Onboarding issues | Track wallet types |
| 10MB file uploads sufficient | Increase limit | Monitor upload sizes |

### 9.3 Known MVP Limitations

| Limitation | User Impact | Communication Plan |
|------------|-------------|-------------------|
| Testnet only | No real earnings | Clear UI indicators |
| Manual dispute resolution | Slow resolution | Set expectations (48hr) |
| No mobile app | Web only | Responsive design helps |

---

## 10. MVP Work Item Breakdown

### 10.1 Work Item Summary

| Priority | Count | Total Effort |
|----------|-------|--------------|
| P0 (Must Have) | 8 | ~32 hours |
| P1 (Should Have) | 6 | ~24 hours |
| P2 (Nice to Have) | 4 | ~16 hours |
| **Total MVP** | 18 | ~72 hours |

### 10.2 Prioritization Framework

**P0 — Must Have (MVP Blockers)**
- Without this, MVP cannot function or validate hypothesis
- Zero flexibility on scope

**P1 — Should Have (MVP Expected)**
- Significantly improves MVP value/experience
- Can be descoped if timeline critical

**P2 — Nice to Have (MVP Polish)**
- Improves quality but not essential for validation
- First to cut if needed

### 10.3 Detailed Work Items

---

#### Epic: Core Submission Flow

_Complete the worker submission pipeline with IPFS uploads and contract payments._

#### [WORK-001] Wire IPFS Upload in Submission Endpoint

- **Priority:** P0
- **Type:** Backend Integration
- **Description:** Connect the existing IPFSService to the subtask submission endpoint. Currently has a TODO placeholder returning fake hash.
- **Acceptance Criteria:**
  - [ ] Uploaded files are stored on IPFS via Pinata
  - [ ] IPFS hash is saved to submission.artifact_ipfs_hash
  - [ ] Supports JSON, CSV, MD file types
  - [ ] Max file size 10MB enforced
  - [ ] Error handling for upload failures
- **Technical Approach:** 
  1. Import IPFSService in subtasks.py
  2. Read file content from UploadFile
  3. Call ipfs_service.pin_file()
  4. Store returned hash in submission record
- **Dependencies:** None (IPFSService exists)
- **Effort Estimate:** S (2-4 hours)
- **Skills Required:** Backend (Python)
- **Risks:** Pinata API rate limits
- **Full Spec Reference:** Section 5.3 Pinata Integration

---

#### [WORK-002] Deploy Smart Contracts to Base Sepolia

- **Priority:** P0
- **Type:** Infrastructure
- **Description:** Deploy FlowEscrow, FlowArtifactRegistry, and MockCNGN to Base Sepolia testnet.
- **Acceptance Criteria:**
  - [ ] All 3 contracts deployed successfully
  - [ ] Contract addresses saved to backend .env
  - [ ] Contracts verified on BaseScan
  - [ ] MockCNGN has minted test tokens
  - [ ] Deployment script documented
- **Technical Approach:**
  1. Set up deployer wallet with Sepolia ETH
  2. Run forge script with --broadcast
  3. Verify contracts using forge verify-contract
  4. Update .env with addresses
- **Dependencies:** None
- **Effort Estimate:** S (2-3 hours)
- **Skills Required:** DevOps, Solidity
- **Risks:** Sepolia faucet availability
- **Full Spec Reference:** Section 4 Smart Contracts

---

#### [WORK-003] Wire Contract Calls in Backend

- **Priority:** P0
- **Type:** Backend Integration
- **Description:** Connect backend approval endpoint to FlowEscrow.approveSubtask() contract call.
- **Acceptance Criteria:**
  - [ ] On subtask approval, backend calls approveSubtask on escrow
  - [ ] Worker receives payment (MockCNGN transfer)
  - [ ] Transaction hash saved to submission.payment_tx_hash
  - [ ] Error handling for failed transactions
  - [ ] Retry logic with exponential backoff
- **Technical Approach:**
  1. Update BlockchainService with contract ABI
  2. Add approve_subtask_payment() method
  3. Call from subtasks.py approve endpoint
  4. Handle Web3 exceptions
- **Dependencies:** WORK-002 (contracts deployed)
- **Effort Estimate:** M (4-6 hours)
- **Skills Required:** Backend (Python, Web3)
- **Risks:** Gas estimation, nonce management
- **Full Spec Reference:** Section 4.1 FlowEscrow

---

#### [WORK-004] Frontend Submission Modal Component

- **Priority:** P0
- **Type:** Frontend
- **Description:** Create a modal component for workers to submit their completed work with file upload.
- **Acceptance Criteria:**
  - [ ] Modal opens from TaskDetail page for claimed subtasks
  - [ ] Text area for content summary (required)
  - [ ] File upload input (accepts .json, .csv, .md)
  - [ ] File size validation (max 10MB)
  - [ ] Submit button with loading state
  - [ ] Success/error feedback
  - [ ] Modal closes on success, refreshes subtask status
- **Technical Approach:**
  1. Create SubmitWorkModal.tsx component
  2. Use react-dropzone or native file input
  3. Call subtaskService.submit() with FormData
  4. Handle loading/error states
- **Dependencies:** WORK-001 (backend accepts files)
- **Effort Estimate:** M (4-6 hours)
- **Skills Required:** Frontend (React, TypeScript)
- **Risks:** File upload UX on mobile
- **Full Spec Reference:** Section 3.3 Subtask Workflow

---

#### [WORK-005] Frontend Review Actions (Approve/Reject)

- **Priority:** P0
- **Type:** Frontend
- **Description:** Add approve/reject buttons on TaskDetail for admins reviewing submissions.
- **Acceptance Criteria:**
  - [ ] Admin sees "Approve" and "Reject" buttons on submitted subtasks
  - [ ] Approve triggers backend approval + contract payment
  - [ ] Reject shows modal for review notes (required)
  - [ ] Loading states during API calls
  - [ ] Success feedback with transaction hash display
  - [ ] Status updates after action
- **Technical Approach:**
  1. Add ReviewActions component to TaskDetail
  2. Conditionally render for admin users
  3. Call subtaskService.approve/reject
  4. Display tx hash on success
- **Dependencies:** WORK-003 (backend wired to contract)
- **Effort Estimate:** M (4-5 hours)
- **Skills Required:** Frontend (React, TypeScript)
- **Risks:** None significant
- **Full Spec Reference:** Section 3.3 Submission Review

---

#### [WORK-006] Task Funding Flow (Contract Integration)

- **Priority:** P0
- **Type:** Full Stack
- **Description:** Wire task funding to escrow contract - frontend triggers approval + fundTask, backend records tx hash.
- **Acceptance Criteria:**
  - [ ] Admin can fund task from TaskDetail page
  - [ ] Frontend prompts wallet to approve MockCNGN spend
  - [ ] Frontend calls fundTask on escrow contract
  - [ ] Backend records escrow_tx_hash on task
  - [ ] Task status updates to "funded"
  - [ ] Error handling for rejected/failed transactions
- **Technical Approach:**
  1. Add FundTaskButton component using wagmi hooks
  2. useContractWrite for approve + fundTask
  3. On success, call backend /tasks/{id}/fund with tx hash
  4. Backend updates task status
- **Dependencies:** WORK-002 (contracts deployed)
- **Effort Estimate:** M (5-6 hours)
- **Skills Required:** Frontend (React, wagmi), Backend
- **Risks:** Wallet UX for two-transaction flow
- **Full Spec Reference:** Section 3.2 Task Funding

---

#### [WORK-007] Error Handling & Loading States (Frontend)

- **Priority:** P0
- **Type:** Frontend
- **Description:** Add consistent loading states and error handling across all pages.
- **Acceptance Criteria:**
  - [ ] All API calls show loading spinners
  - [ ] Errors display user-friendly toast messages
  - [ ] Network errors handled gracefully
  - [ ] Retry option for failed requests
  - [ ] No unhandled promise rejections
- **Technical Approach:**
  1. Add react-hot-toast for notifications
  2. Create useApiCall hook with loading/error state
  3. Wrap existing API calls
  4. Add error boundary component
- **Dependencies:** None
- **Effort Estimate:** M (4-5 hours)
- **Skills Required:** Frontend (React)
- **Risks:** None
- **Full Spec Reference:** Section 5.1 Performance

---

#### [WORK-008] Backend Tests for Subtask Flow

- **Priority:** P0
- **Type:** Testing
- **Description:** Add integration tests for claim → submit → approve flow.
- **Acceptance Criteria:**
  - [ ] Test subtask claim endpoint
  - [ ] Test submission endpoint with mock file
  - [ ] Test approval endpoint
  - [ ] Test rejection endpoint
  - [ ] Test dispute creation
  - [ ] All tests pass in CI
  - [ ] Coverage > 80% for subtasks module
- **Technical Approach:**
  1. Create tests/integration/test_subtasks.py
  2. Use pytest fixtures for test data
  3. Mock IPFS and blockchain services
  4. Test happy path + error cases
- **Dependencies:** None
- **Effort Estimate:** M (4-6 hours)
- **Skills Required:** Backend (Python, pytest)
- **Risks:** None
- **Full Spec Reference:** Section 10 Testing Strategy

---

#### Epic: Admin & Management

_Enable platform administration and task management._

#### [WORK-009] Task Creation Form (Frontend)

- **Priority:** P1
- **Type:** Frontend
- **Description:** Create admin UI for creating new research tasks.
- **Acceptance Criteria:**
  - [ ] Form with all task fields (title, description, question, budget, deadline, skills)
  - [ ] Validation for required fields
  - [ ] Submit creates task in draft status
  - [ ] Option to trigger AI decomposition after creation
  - [ ] Success redirects to task detail page
- **Technical Approach:**
  1. Create TaskCreatePage or modal
  2. Use react-hook-form for validation
  3. Call taskService.create()
  4. Optionally chain decompose call
- **Dependencies:** None
- **Effort Estimate:** M (4-5 hours)
- **Skills Required:** Frontend (React, TypeScript)
- **Risks:** None
- **Full Spec Reference:** Section 3.2 Task Creation

---

#### [WORK-010] AI Decomposition UI

- **Priority:** P1
- **Type:** Frontend
- **Description:** Add UI to trigger and preview AI task decomposition.
- **Acceptance Criteria:**
  - [ ] "Decompose with AI" button on draft tasks
  - [ ] Loading state during AI processing (can take 10-30s)
  - [ ] Preview generated subtasks before confirming
  - [ ] Option to edit subtasks before saving
  - [ ] Confirm saves subtasks to database
- **Technical Approach:**
  1. Add DecomposeButton component
  2. Call taskService.decompose()
  3. Show preview modal with subtask list
  4. Allow inline editing
  5. Confirm creates subtasks
- **Dependencies:** None (backend endpoint exists)
- **Effort Estimate:** M (4-5 hours)
- **Skills Required:** Frontend (React)
- **Risks:** Long AI response times
- **Full Spec Reference:** Section 3.2 AI Task Decomposition

---

#### [WORK-011] Admin Panel - User List Enhancement

- **Priority:** P1
- **Type:** Frontend
- **Description:** Enhance admin user list with search, filter, and verify actions.
- **Acceptance Criteria:**
  - [ ] Search users by name or wallet
  - [ ] Filter by verified/unverified
  - [ ] "Verify" button marks user as verified
  - [ ] "Ban" button with reason input
  - [ ] Pagination for large lists
- **Technical Approach:**
  1. Enhance Admin.tsx with filters
  2. Add search input with debounce
  3. Add action buttons with confirmation
  4. Call admin endpoints
- **Dependencies:** None (endpoints exist)
- **Effort Estimate:** S (3-4 hours)
- **Skills Required:** Frontend (React)
- **Risks:** None
- **Full Spec Reference:** Section 3.7 Admin Features

---

#### [WORK-012] Admin Panel - Dispute View

- **Priority:** P1
- **Type:** Frontend
- **Description:** Add dispute listing and basic resolution UI for admins.
- **Acceptance Criteria:**
  - [ ] List all disputes with status filter
  - [ ] Show dispute details (subtask, parties, reason)
  - [ ] Resolution form with notes
  - [ ] Award to worker or client option
  - [ ] Status updates after resolution
- **Technical Approach:**
  1. Add Disputes tab to Admin page
  2. Fetch disputes from admin endpoint
  3. Create DisputeCard component
  4. Add resolution modal
- **Dependencies:** None (backend exists)
- **Effort Estimate:** M (4-5 hours)
- **Skills Required:** Frontend (React)
- **Risks:** None
- **Full Spec Reference:** Section 3.7 Dispute Resolution

---

#### [WORK-013] Worker Dashboard Enhancements

- **Priority:** P1
- **Type:** Frontend
- **Description:** Enhance worker dashboard with submission history and earnings.
- **Acceptance Criteria:**
  - [ ] Show all user's submissions with status
  - [ ] Display total earnings (sum of approved payments)
  - [ ] Show pending payments (approved but not yet paid)
  - [ ] Link to view submission details
  - [ ] Refresh data on mount
- **Technical Approach:**
  1. Add submissions query to Dashboard
  2. Create EarningsSummary component
  3. Create SubmissionHistory component
  4. Calculate totals from submission data
- **Dependencies:** None
- **Effort Estimate:** S (3-4 hours)
- **Skills Required:** Frontend (React)
- **Risks:** None
- **Full Spec Reference:** Section 4.2 Worker Dashboard

---

#### [WORK-014] Profile Edit Form

- **Priority:** P1
- **Type:** Frontend
- **Description:** Allow users to edit their profile (name, bio, skills).
- **Acceptance Criteria:**
  - [ ] Edit form on Profile page
  - [ ] Pre-populated with current values
  - [ ] Skills multi-select from predefined list
  - [ ] Save button updates profile
  - [ ] Success feedback
- **Technical Approach:**
  1. Add edit mode to Profile page
  2. Use react-hook-form
  3. Call userService.updateProfile()
  4. Refresh user state on success
- **Dependencies:** None
- **Effort Estimate:** S (2-3 hours)
- **Skills Required:** Frontend (React)
- **Risks:** None
- **Full Spec Reference:** Section 3.1 Profile Setup

---

#### Epic: Quality & Polish

_Improve code quality and developer experience._

#### [WORK-015] Alembic Migration Setup

- **Priority:** P2
- **Type:** Infrastructure
- **Description:** Replace create_all() with proper Alembic migrations.
- **Acceptance Criteria:**
  - [ ] Initial migration capturing current schema
  - [ ] Migration runs successfully on fresh database
  - [ ] setup_db.py uses alembic upgrade head
  - [ ] Migration documented in README
- **Technical Approach:**
  1. Run alembic revision --autogenerate
  2. Review and clean up generated migration
  3. Test on fresh database
  4. Update setup scripts
- **Dependencies:** None
- **Effort Estimate:** S (2-3 hours)
- **Skills Required:** Backend (Python, Alembic)
- **Risks:** Schema drift if models changed
- **Full Spec Reference:** Section 6 Directory Structure

---

#### [WORK-016] API Rate Limiting

- **Priority:** P2
- **Type:** Backend
- **Description:** Add rate limiting to AI endpoints and auth endpoints.
- **Acceptance Criteria:**
  - [ ] AI endpoints: 10 requests/minute per user
  - [ ] Auth endpoints: 5 requests/minute per IP
  - [ ] 429 response with retry-after header
  - [ ] Configurable via environment
- **Technical Approach:**
  1. Add slowapi or fastapi-limiter
  2. Configure limits per route
  3. Add middleware
  4. Test rate limit behavior
- **Dependencies:** None
- **Effort Estimate:** S (2-3 hours)
- **Skills Required:** Backend (Python)
- **Risks:** None
- **Full Spec Reference:** Section 5.2 Security

---

#### [WORK-017] Frontend Unit Tests

- **Priority:** P2
- **Type:** Testing
- **Description:** Add unit tests for critical frontend components.
- **Acceptance Criteria:**
  - [ ] Test ConnectButton component
  - [ ] Test auth store actions
  - [ ] Test API service mocking
  - [ ] Coverage > 60% for tested modules
  - [ ] Tests run in CI
- **Technical Approach:**
  1. Set up Vitest with React Testing Library
  2. Create test files for key components
  3. Mock API responses
  4. Add to CI pipeline
- **Dependencies:** None
- **Effort Estimate:** M (4-5 hours)
- **Skills Required:** Frontend (React, Vitest)
- **Risks:** None
- **Full Spec Reference:** Section 10.3 Frontend Tests

---

#### [WORK-018] Documentation Update

- **Priority:** P2
- **Type:** Documentation
- **Description:** Update README with complete setup and deployment instructions.
- **Acceptance Criteria:**
  - [ ] Contract deployment instructions
  - [ ] Environment variable documentation
  - [ ] Local development setup (all services)
  - [ ] Testnet deployment guide
  - [ ] API documentation link
- **Technical Approach:**
  1. Review and update README.md
  2. Add DEPLOYMENT.md if needed
  3. Document all env vars
  4. Add troubleshooting section
- **Dependencies:** All other work items (document final state)
- **Effort Estimate:** S (2-3 hours)
- **Skills Required:** Technical Writing
- **Risks:** None
- **Full Spec Reference:** README.md

---

### 10.4 Work Item Dependency Graph

```
[WORK-002] Deploy Contracts
     │
     ├──────────────────────────┐
     ▼                          ▼
[WORK-003] Wire Backend    [WORK-006] Task Funding
     │
     ▼
[WORK-005] Review Actions

[WORK-001] IPFS Upload
     │
     ▼
[WORK-004] Submit Modal

[WORK-007] Error Handling ─── (parallel, no deps)
[WORK-008] Backend Tests  ─── (parallel, no deps)
[WORK-009] Task Create    ─── (parallel, no deps)
[WORK-010] AI Decompose   ─── (parallel, no deps)
[WORK-011] Admin Users    ─── (parallel, no deps)
[WORK-012] Disputes       ─── (parallel, no deps)
[WORK-013] Dashboard      ─── (parallel, no deps)
[WORK-014] Profile Edit   ─── (parallel, no deps)
[WORK-015] Alembic        ─── (parallel, no deps)
[WORK-016] Rate Limiting  ─── (parallel, no deps)
[WORK-017] Frontend Tests ─── (parallel, no deps)
[WORK-018] Documentation  ─── (after all others)
```

### 10.5 Suggested Implementation Sequence

#### Phase 1: Core Pipeline [Days 1-3]

| Order | Work Item | Effort | Dependency |
|-------|-----------|--------|------------|
| 1 | [WORK-001] IPFS Upload | S | None |
| 2 | [WORK-002] Deploy Contracts | S | None |
| 3 | [WORK-003] Wire Contract Calls | M | WORK-002 |
| 4 | [WORK-004] Submit Modal | M | WORK-001 |
| 5 | [WORK-005] Review Actions | M | WORK-003 |
| 6 | [WORK-006] Task Funding | M | WORK-002 |

**Phase 1 Milestone:** Complete end-to-end flow: fund task → claim → submit → approve → payment

#### Phase 2: Quality & Admin [Days 4-5]

| Order | Work Item | Effort | Dependency |
|-------|-----------|--------|------------|
| 1 | [WORK-007] Error Handling | M | None |
| 2 | [WORK-008] Backend Tests | M | None |
| 3 | [WORK-009] Task Create Form | M | None |
| 4 | [WORK-010] AI Decompose UI | M | None |

**Phase 2 Milestone:** Admin can create tasks, robust error handling, test coverage

#### Phase 3: Polish & Ship [Days 6-7]

| Order | Work Item | Effort | Dependency |
|-------|-----------|--------|------------|
| 1 | [WORK-011] Admin Users | S | None |
| 2 | [WORK-012] Disputes | M | None |
| 3 | [WORK-013] Dashboard | S | None |
| 4 | [WORK-014] Profile Edit | S | None |
| 5 | [WORK-015] Alembic | S | None |
| 6 | [WORK-018] Documentation | S | All |

**Phase 3 Milestone:** MVP Complete - ready for beta testing

### 10.6 Work Items by Skill/Team

| Skill Area | Work Items | Total Effort |
|------------|------------|--------------|
| Backend | WORK-001, 003, 008, 015, 016 | ~18 hours |
| Frontend | WORK-004, 005, 006, 007, 009, 010, 011, 012, 013, 014, 017 | ~42 hours |
| DevOps/Contracts | WORK-002 | ~3 hours |
| Documentation | WORK-018 | ~3 hours |

---

## 11. MVP to Full Spec Migration Path

### 11.1 Post-MVP Roadmap

| Phase | Features/Capabilities | Technical Work | Trigger |
|-------|----------------------|----------------|---------|
| MVP+1 | ID verification, artifact creation | KYC integration, artifact aggregation | 50+ users |
| MVP+2 | Artifact marketplace, royalties | Payment splitting, licensing | 10+ artifacts |
| Full | Real-time updates, PWA, analytics | WebSockets, service worker, BI tools | Production launch |

### 11.2 Technical Debt Register

| Debt Item | Incurred In | Impact | Remediation | Priority |
|-----------|-------------|--------|-------------|----------|
| Hardcoded claim limits | WORK-004 | Inflexible | Add settings table | Low |
| Sync contract calls | WORK-003 | Slower approvals | Event queue | Medium |
| No caching | All | Higher latency | Add Redis | Medium |

### 11.3 Architecture Evolution Points

| Component | MVP State | Evolution Trigger | Target State |
|-----------|-----------|-------------------|--------------|
| Contract calls | Sync via backend | >10 tx/minute | Event-driven queue |
| Caching | None | Response times >500ms | Redis cache |
| Real-time | Polling | User complaints | WebSocket |

---

## 12. MVP Risk Register

| Risk | Probability | Impact | Mitigation | Contingency |
|------|-------------|--------|------------|-------------|
| Pinata API down | Low | High | Retry logic, mock fallback | Manual file handling |
| Contract bug | Low | Critical | Comprehensive tests | Pause contract, redeploy |
| Gas price spike | Medium | Medium | Gas estimation buffer | Adjust platform fees |
| Worker no-shows | Medium | Medium | Claim expiry (48h) | Admin can unclaim |
| AI rate limits | Low | Medium | Caching, queue | Fallback prompts |

---

## 13. Appendix

### A. MVP vs Full Spec Field-by-Field Comparison

All database fields are implemented — no schema differences between MVP and full spec.

### B. Deferred Work Items (Post-MVP Backlog)

| ID | Item | Reason Deferred | Priority Post-MVP | Depends On |
|----|------|-----------------|-------------------|------------|
| POST-001 | ID Verification | Not blocking core flow | P1 | Admin panel |
| POST-002 | Artifact Marketplace | Need artifacts first | P0 | Task completion |
| POST-003 | Royalty Distribution | Complex | P1 | Marketplace |
| POST-004 | PWA Offline | Not critical | P2 | None |
| POST-005 | Analytics Dashboard | Need data | P1 | Data collection |
| POST-006 | Auto-approval | Need baseline | P1 | 100+ submissions |

### C. Contract Addresses (To be filled after deployment)

```
Base Sepolia:
- FlowEscrow: 0x...
- FlowArtifactRegistry: 0x...
- MockCNGN: 0x...
```

### D. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 2025 | AI | Initial MVP specification |
