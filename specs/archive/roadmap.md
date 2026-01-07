# Flow Platform Roadmap

## Current Status Overview

```
Phase 1: Foundation        ████████████████████ 100%
Phase 2: Core Backend      ████████████░░░░░░░░  60%
Phase 3: External Integr.  ████░░░░░░░░░░░░░░░░  20%
Phase 4: Frontend          ████████░░░░░░░░░░░░  40%
Phase 5: Integration       ░░░░░░░░░░░░░░░░░░░░   0%
```

## Detailed Progress

### Phase 1: Foundation ✅ COMPLETE

| Item | Status | Notes |
|------|--------|-------|
| 1.1 Backend project structure | ✅ Done | FastAPI app with routes, models, schemas |
| 1.2 Database models | ✅ Done | User, Task, Subtask, Submission, Artifact, Dispute |
| 1.3 Smart contracts | ✅ Done | FlowEscrow, FlowArtifactRegistry (not deployed) |
| 1.4 Frontend project structure | ✅ Done | React + Vite + TailwindCSS + wagmi |
| 1.5 Docker setup | ✅ Done | PostgreSQL via docker-compose |
| 1.6 Dev scripts | ✅ Done | run_dev.sh, run_tests.sh, setup_db.py |

### Phase 2: Core Backend 🔄 IN PROGRESS

| Item | Status | Notes |
|------|--------|-------|
| 2.1 Auth endpoints | ✅ Done | Nonce generation, signature verification, JWT |
| 2.2 User endpoints | ✅ Done | Profile CRUD, basic queries |
| 2.3 Task endpoints | ✅ Done | List, get, create (admin), fund |
| 2.4 Subtask endpoints | ⚠️ Partial | List, get done; claim/submit need work |
| 2.5 Blockchain integration | ❌ Not started | Contract interactions not wired |

### Phase 3: External Integrations 🔄 IN PROGRESS

| Item | Status | Notes |
|------|--------|-------|
| 3.1 IPFS/Pinata | ⚠️ Partial | Service exists, not fully integrated |
| 3.2 AI/Claude | ⚠️ Partial | Basic service, decomposition works |
| 3.3 Paper APIs | ⚠️ Partial | Semantic Scholar service exists |
| 3.4 Contract events | ❌ Not started | No event monitoring |

### Phase 4: Frontend 🔄 IN PROGRESS

| Item | Status | Notes |
|------|--------|-------|
| 4.1 Auth flow | ⚠️ Partial | Wallet connect works, full auth flow incomplete |
| 4.2 Task pages | ✅ Done | Task list, task detail with subtasks |
| 4.3 Worker portal | ❌ Not started | Dashboard exists but no functionality |
| 4.4 Admin panel | ❌ Not started | Page exists, no features |
| 4.5 PWA setup | ❌ Not started | Vite PWA plugin installed, not configured |

### Phase 5: Integration & Testing ❌ NOT STARTED

| Item | Status | Notes |
|------|--------|-------|
| 5.1 End-to-end flows | ❌ Not started | No E2E tests |
| 5.2 Contract integration | ❌ Not started | Contracts not deployed |
| 5.3 Documentation | ⚠️ Partial | specs/ folder created |

---

## Recommended Next Steps

### Immediate Priority (This Week)

1. **Enhanced Task/Subtask Content** - Implement specs/enhanced-tasks.md
   - Add rich descriptions, attachments, references
   - Make subtasks actionable with clear deliverables
   
2. **Complete Subtask Flow**
   - Claim subtask (with wallet auth)
   - Submit work (with file upload)
   - Approve/reject submissions

3. **Worker Dashboard**
   - Show claimed subtasks
   - Submission status tracking
   - Earnings summary

### Short Term (Next 2 Weeks)

4. **Full Auth Flow**
   - Connect wallet → Check if user exists
   - If not, create profile flow
   - Store JWT, maintain session

5. **Admin Panel**
   - User verification
   - Task creation wizard
   - Dispute management

6. **AI Integration**
   - Task decomposition UI
   - Paper discovery in subtask view
   - Claim extraction tools

### Medium Term (Month 1)

7. **Smart Contract Deployment**
   - Deploy to Base Sepolia
   - Wire up escrow funding
   - Payment release on approval

8. **IPFS Integration**
   - File uploads for attachments
   - Artifact storage
   - Content verification

9. **PWA Features**
   - Offline support
   - Push notifications
   - Install prompt

### Launch Checklist

- [ ] User can connect wallet and create profile
- [ ] Admin can create tasks with rich content
- [ ] Tasks can be funded via escrow
- [ ] AI decomposes tasks into subtasks
- [ ] Workers can claim subtasks
- [ ] Workers can submit work with files
- [ ] Clients can approve/reject submissions
- [ ] Payments release automatically
- [ ] Artifacts stored on IPFS
- [ ] Basic reputation tracking
- [ ] Admin can manage disputes
- [ ] All tests pass
- [ ] Deployed to testnet

---

## Tech Debt & Improvements

| Item | Priority | Notes |
|------|----------|-------|
| Alembic migrations | High | Currently using create_all(), need proper migrations |
| Error handling | High | Need consistent error responses |
| Input validation | Medium | More thorough Pydantic validation |
| Logging | Medium | Structured logging needed |
| Rate limiting | Medium | Protect AI endpoints |
| Caching | Low | Redis for session/query caching |
| Monitoring | Low | Health checks, metrics |

---

## Architecture Decisions Pending

1. **File Storage Strategy**
   - Direct IPFS upload vs backend proxy?
   - Max file sizes?
   - Allowed file types?

2. **Real-time Updates**
   - WebSockets for live status?
   - Polling sufficient for MVP?

3. **AI Cost Management**
   - Per-user limits?
   - Caching strategy?
   - Fallback when rate limited?

4. **Payment Flow**
   - Automatic release on approval?
   - Manual release option?
   - Dispute window duration?
