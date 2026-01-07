# Flow Platform - Product Specification

## 1. Executive Summary

Flow is a decentralized research synthesis platform connecting knowledge workers with research clients. Workers earn cryptocurrency by completing AI-decomposed research subtasks, while clients receive verified research outputs. Completed work aggregates into licensable artifacts (datasets, knowledge graphs) that generate recurring revenue for contributors.

### Product Vision
Democratize access to research capabilities by enabling anyone with domain expertise to contribute to and earn from academic research synthesis.

### Target Launch
Q1 2025 - MVP on Base Sepolia testnet

---

## 2. User Personas

### 2.1 Knowledge Worker (Primary)
**Name**: Adaeze  
**Location**: Lagos, Nigeria  
**Background**: Final-year university student studying Public Health  
**Goals**:
- Earn supplemental income using academic skills
- Build verifiable portfolio of research work
- Gain experience with AI tools and blockchain

**Pain Points**:
- Limited well-paying remote work opportunities
- Traditional freelance platforms have high fees and slow payments
- No way to prove research skills to potential employers

**Tech Profile**:
- Android smartphone, intermittent broadband
- Familiar with mobile money (OPay, Palmpay)
- New to crypto but motivated to learn

### 2.2 Research Client (Secondary)
**Name**: Dr. Okonkwo  
**Location**: Abuja, Nigeria  
**Background**: Health policy researcher at NGO  
**Goals**:
- Commission literature reviews efficiently
- Get structured data from research papers
- Ensure outputs are verifiable and citable

**Pain Points**:
- Limited budget for traditional research consultants
- Difficulty finding reliable research assistants
- No visibility into work progress

### 2.3 Artifact Consumer (Tertiary)
**Name**: TechCorp Analytics Team  
**Location**: Global  
**Background**: AI company building health domain models  
**Goals**:
- Access curated, verified research datasets
- Clear licensing and provenance
- Regular updates as new research is processed

---

## 3. Feature Specifications

### 3.1 Authentication & Identity

#### F-AUTH-01: Wallet-Based Login
**Priority**: P0 (Must Have)  
**Status**: Implemented

**Description**: Users authenticate by signing a message with their Ethereum wallet.

**User Flow**:
1. User clicks "Connect Wallet"
2. Wallet selection modal appears (MetaMask, WalletConnect, Coinbase Wallet)
3. User approves connection
4. Backend generates unique nonce
5. User signs message containing nonce
6. Backend verifies signature, issues JWT
7. User redirected to dashboard

**Acceptance Criteria**:
- [ ] Supports MetaMask, WalletConnect, Coinbase Wallet
- [ ] Nonce expires after 5 minutes
- [ ] JWT valid for 24 hours with refresh capability
- [ ] Works on mobile browsers with wallet apps

#### F-AUTH-02: Profile Setup
**Priority**: P0 (Must Have)  
**Status**: Implemented

**Description**: First-time users complete profile with name, country, skills.

**Required Fields**:
- Display name (3-50 characters)
- Country (ISO 2-letter code)
- Skills (select from predefined list + custom)

**Optional Fields**:
- Bio (max 500 characters)
- Profile photo (IPFS upload)

#### F-AUTH-03: ID Verification
**Priority**: P1 (Should Have)  
**Status**: Not Started

**Description**: Optional KYC for premium features and higher task limits.

**Flow**:
1. User uploads national ID document
2. System hashes document (not stored)
3. Admin reviews and approves
4. User receives "Verified" badge

---

### 3.2 Task Management

#### F-TASK-01: Task Creation (Admin)
**Priority**: P0 (Must Have)  
**Status**: Implemented

**Description**: Admins create research tasks with rich content.

**Task Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title (max 500 chars) |
| description | text | Yes | Detailed task description |
| description_html | text | No | Rich HTML version |
| research_question | text | Yes | Core question to answer |
| background_context | text | No | Additional context |
| total_budget_cngn | decimal | Yes | Budget in cNGN |
| skills_required | string[] | No | Required worker skills |
| deadline | datetime | Yes | Task deadline |
| references | json[] | No | Links to relevant papers/resources |
| attachments | json[] | No | Supporting files |
| expected_outcomes | string[] | No | List of deliverables |
| methodology_notes | text | No | Suggested approach |

#### F-TASK-02: Task Funding
**Priority**: P0 (Must Have)  
**Status**: Partial

**Description**: Client funds task via escrow smart contract.

**Flow**:
1. Client approves cNGN spend to Escrow contract
2. Client calls `fundTask(taskId, amount)`
3. Backend receives event, updates task status to "funded"
4. Task becomes visible to workers

**Acceptance Criteria**:
- [ ] Frontend shows funding transaction status
- [ ] Task status updates automatically on confirmation
- [ ] Refund mechanism for cancelled tasks

#### F-TASK-03: AI Task Decomposition
**Priority**: P0 (Must Have)  
**Status**: Partial

**Description**: AI breaks task into atomic subtasks.

**Subtask Types**:
| Type | Description | Typical Budget % |
|------|-------------|------------------|
| discovery | Find relevant papers/sources | 15-20% |
| extraction | Extract claims from sources | 25-30% |
| mapping | Build relationships between claims | 20-25% |
| assembly | Combine into structured output | 15-20% |
| narrative | Write human-readable synthesis | 15-20% |

**AI Prompt Structure**:
```
Given this research task:
- Title: {title}
- Question: {research_question}
- Context: {background_context}

Decompose into 3-7 subtasks covering: discovery, extraction, mapping, assembly, narrative.
For each subtask provide: title, description, type, budget_percent, estimated_hours, acceptance_criteria.
```

#### F-TASK-04: Task Listing & Search
**Priority**: P0 (Must Have)  
**Status**: Implemented

**Description**: Workers browse available tasks.

**Filters**:
- Status (funded, in_progress, completed)
- Skills required
- Budget range
- Deadline
- Sort by: newest, deadline, budget

---

### 3.3 Subtask Workflow

#### F-SUB-01: Subtask Claiming
**Priority**: P0 (Must Have)  
**Status**: Partial

**Description**: Worker claims a subtask to work on it.

**Rules**:
- Worker can claim max 3 active subtasks
- Worker must have matching skills (if specified)
- Worker must be verified for tasks >50,000 cNGN
- Claim expires after 48 hours if no submission

**Flow**:
1. Worker clicks "Claim" on subtask
2. System checks eligibility
3. Subtask status changes to "claimed"
4. Worker has 48 hours to submit (extendable)

#### F-SUB-02: Work Submission
**Priority**: P0 (Must Have)  
**Status**: Partial

**Description**: Worker submits completed work.

**Submission Contents**:
- Summary (what was done)
- Artifact file (JSON, CSV, or Markdown)
- Optional supporting files

**Flow**:
1. Worker uploads artifact to IPFS
2. Worker submits with summary
3. Submission status = "pending"
4. Client/Admin reviews

**Acceptance Criteria**:
- [ ] File upload to IPFS works reliably
- [ ] Preview of submission before submit
- [ ] Worker can update pending submission

#### F-SUB-03: Submission Review
**Priority**: P0 (Must Have)  
**Status**: Partial

**Description**: Client or admin reviews and approves/rejects.

**Review Options**:
- **Approve**: Payment released, subtask complete
- **Reject**: Feedback provided, worker can resubmit
- **Dispute**: Escalate to admin resolution

**Auto-Approval** (optional):
- AI reviews submission against acceptance criteria
- If confidence > 90%, auto-approve
- Admin can disable per-task

#### F-SUB-04: Payment Release
**Priority**: P0 (Must Have)  
**Status**: Not Started

**Description**: Escrow releases payment on approval.

**Flow**:
1. Reviewer approves submission
2. Backend calls `approveSubtask(taskId, subtaskIndex, worker, amount)`
3. Escrow transfers cNGN to worker
4. Worker sees payment in wallet

---

### 3.4 AI Assistance Tools

#### F-AI-01: Paper Discovery
**Priority**: P1 (Should Have)  
**Status**: Partial

**Description**: AI helps find relevant academic papers.

**Sources**:
- Semantic Scholar API
- OpenAlex API
- CrossRef API

**Features**:
- Keyword search with filters (year, venue, citations)
- Save papers to subtask references
- Extract metadata automatically

#### F-AI-02: Claim Extraction
**Priority**: P1 (Should Have)  
**Status**: Partial

**Description**: AI extracts claims from papers.

**Output Format**:
```json
{
  "claim": "Statement extracted from paper",
  "evidence": "Supporting quote or reference",
  "confidence": 0.85,
  "source_section": "Results",
  "page": 7
}
```

#### F-AI-03: Synthesis Generation
**Priority**: P2 (Nice to Have)  
**Status**: Not Started

**Description**: AI generates narrative synthesis from claims.

---

### 3.5 Artifacts & Licensing

#### F-ART-01: Artifact Creation
**Priority**: P1 (Should Have)  
**Status**: Partial

**Description**: Completed tasks produce licensable artifacts.

**Artifact Types**:
- **Dataset**: Structured data (CSV, JSON)
- **Knowledge Graph**: Entity-relationship data
- **Report**: Narrative document

**Creation Flow**:
1. Task completes (all subtasks approved)
2. System aggregates subtask outputs
3. Admin reviews and publishes artifact
4. Artifact registered on-chain

#### F-ART-02: Artifact Licensing
**Priority**: P2 (Nice to Have)  
**Status**: Not Started

**Description**: Users can purchase artifact access.

**Licensing Model**:
- One-time purchase price set by admin
- Revenue split: 80% contributors, 20% platform
- Contributor shares based on subtask budgets

#### F-ART-03: On-Chain Registration
**Priority**: P1 (Should Have)  
**Status**: Partial

**Description**: Artifact hash stored on blockchain for provenance.

**On-Chain Data**:
- Artifact ID
- Content hash (IPFS CID)
- Contributor addresses
- Timestamp

---

### 3.6 Reputation System

#### F-REP-01: Basic Reputation
**Priority**: P1 (Should Have)  
**Status**: Partial

**Description**: Track worker performance.

**Metrics**:
- Tasks completed
- First-submission approval rate
- Average completion time
- Disputes won/lost

**Tiers**:
| Tier | Points | Benefits |
|------|--------|----------|
| New | 0-99 | Basic access |
| Active | 100-499 | Claim 5 subtasks |
| Established | 500-999 | Priority matching |
| Expert | 1000+ | Higher budget tasks |

**Point Allocation**:
- Subtask approved: +10 points
- First-submission approval: +5 bonus
- Subtask rejected: -5 points
- Dispute won: +20 points
- Dispute lost: -20 points

---

### 3.7 Admin Features

#### F-ADMIN-01: User Management
**Priority**: P0 (Must Have)  
**Status**: Partial

**Features**:
- List all users with filters
- View user details and history
- Verify user ID
- Ban/unban users

#### F-ADMIN-02: Dispute Resolution
**Priority**: P1 (Should Have)  
**Status**: Not Started

**Features**:
- View open disputes
- Review submission and feedback
- Award decision to worker or client
- Release/refund escrowed funds

#### F-ADMIN-03: Platform Analytics
**Priority**: P2 (Nice to Have)  
**Status**: Not Started

**Metrics**:
- Active users (daily/weekly/monthly)
- Tasks created/completed
- Total value transacted
- Average completion times

---

## 4. User Flows

### 4.1 New Worker Onboarding
```
Connect Wallet → Sign Message → Create Profile → Browse Tasks → Claim Subtask
```

### 4.2 Complete Subtask
```
View Claimed Subtask → Use AI Tools → Prepare Output → Upload to IPFS → Submit → Await Review → Get Paid
```

### 4.3 Client Creates Task
```
Login → Create Task Draft → Add Details/Attachments → Fund Escrow → AI Decompose → Monitor Progress → Review Submissions → Complete Task
```

### 4.4 Dispute Resolution
```
Worker/Client Raises Dispute → Admin Notified → Review Evidence → Make Decision → Funds Released
```

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Page load: <3 seconds on 3G connection
- API response: <500ms for reads, <2s for AI operations
- Support 100 concurrent users initially

### 5.2 Security
- All API endpoints authenticated (except public reads)
- Rate limiting on AI endpoints (10 req/min)
- Input validation on all user inputs
- HTTPS only

### 5.3 Reliability
- 99% uptime target
- Graceful degradation if external APIs down
- Transaction retry logic for blockchain ops

### 5.4 Mobile Experience
- Responsive design for 320px+ screens
- PWA installable on Android/iOS
- Offline viewing of cached content

---

## 6. Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend Framework | React + Vite | Fast builds, great DX, PWA support |
| Backend Framework | FastAPI | Python for AI libs, async performance |
| Database | PostgreSQL | Reliable, JSONB for flexible schemas |
| Blockchain | Base (L2) | Low fees, Ethereum compatibility |
| Storage | IPFS/Pinata | Decentralized, content-addressed |
| AI Provider | Claude API | Best reasoning for research tasks |
| Payment Token | cNGN (or mock) | Stable value for Nigerian users |

---

## 7. Release Strategy

### Phase 1: Internal Testing (Current)
- Deploy to Base Sepolia
- Team testing all flows
- Fix critical bugs

### Phase 2: Closed Beta
- Invite 20 workers
- 5 test tasks with real outputs
- Gather feedback, iterate

### Phase 3: Open Beta
- Public registration
- Full escrow integration
- Artifact marketplace

### Phase 4: Production
- Mainnet deployment
- Real cNGN integration
- Marketing push

---

## 8. Success Metrics

| Metric | Target (MVP) | Target (3 months) |
|--------|--------------|-------------------|
| Registered workers | 50 | 500 |
| Verified workers | 20 | 100 |
| Tasks completed | 10 | 100 |
| Subtasks processed | 50 | 1000 |
| Artifacts created | 3 | 20 |
| First-submission approval rate | 70% | 85% |
| Average subtask completion | 24h | 12h |
| Platform uptime | 95% | 99% |

---

## 9. Open Items

1. **Pricing Model**: How to price tasks fairly for Nigerian market?
2. **Worker Verification**: Manual vs automated ID verification?
3. **Dispute SLA**: How long for dispute resolution?
4. **Artifact NFTs**: Should artifacts be mintable NFTs?
5. **Collaboration**: How to handle multi-worker subtasks?

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*Status: Active Development*
