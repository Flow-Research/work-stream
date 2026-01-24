# Flow Platform - Brainstorm

## The Idea

**Flow** is a decentralized platform that enables knowledge workers to earn by contributing to AI-assisted academic research synthesis. The platform connects research clients with skilled workers who verify AI outputs, add human expertise, and collaboratively build valuable artifacts (datasets, knowledge graphs) that generate recurring revenue through licensing.

## Problem Statement

### For Researchers & Organizations
- Academic research synthesis is time-consuming and expensive
- Quality control for large-scale literature reviews is difficult
- No easy way to access structured research data
- AI outputs need human verification for reliability

### For Knowledge Workers (especially in developing markets)
- Limited access to meaningful remote work opportunities
- Skills in data collection, verification, and research underutilized
- Payment systems often exclude workers without traditional banking
- No way to build reputation and earn from expertise

### For the AI/Research Ecosystem
- AI-generated research summaries need human verification
- High-quality training data for research domains is scarce
- No incentive structure for collaborative knowledge building
- Research artifacts are siloed, not reusable

## The Solution

A three-sided marketplace that:

1. **Decomposes research tasks** - Clients post research questions, AI breaks them into atomic subtasks (discovery, extraction, mapping, assembly, narrative)

2. **Enables micro-work with macro-impact** - Workers claim subtasks matching their skills, complete them with AI assistance, earn crypto payments instantly

3. **Creates reusable artifacts** - Completed work aggregates into datasets and knowledge graphs that can be licensed for recurring revenue

4. **Uses blockchain for trust** - Payments escrowed in smart contracts, artifacts registered on-chain for provenance, disputes resolved transparently

## Target Users

### Primary: Knowledge Workers
- Location: Initially Nigeria (expanding to other African countries)
- Profile: University students, researchers, data collectors, survey professionals
- Motivation: Earn income using existing skills, build portable reputation
- Tech comfort: Smartphone access, familiar with mobile money

### Secondary: Research Clients
- Organizations needing literature reviews, market research, data collection
- Academic institutions with research budgets
- Companies requiring structured market intelligence

### Tertiary: Artifact Consumers
- Researchers needing curated datasets
- AI companies needing training data
- Organizations wanting knowledge graphs for decision-making

## Core Value Propositions

### For Workers
- **Instant payments** - Crypto settles immediately, no waiting for bank transfers
- **Skill matching** - AI matches tasks to worker capabilities
- **Reputation building** - On-chain track record opens more opportunities
- **Royalty income** - Earn ongoing revenue from artifacts you contributed to

### For Clients
- **Cost efficiency** - Distributed workforce reduces research costs
- **Quality assurance** - Multi-layer verification (AI + human + peer review)
- **Speed** - Parallel task completion accelerates timelines
- **Transparency** - Full audit trail of work and approvals

### For the Ecosystem
- **Verified data** - Human-checked research outputs
- **Structured artifacts** - Machine-readable knowledge graphs
- **Open marketplace** - Anyone can build on top of artifacts

## Key Features (MVP)

1. **Wallet-based authentication** - No passwords, just connect wallet
2. **Task decomposition** - AI breaks research questions into subtasks
3. **Subtask marketplace** - Browse, filter, claim work
4. **AI-assisted completion** - Paper discovery, claim extraction tools
5. **Smart contract escrow** - Funds held until work approved
6. **IPFS artifact storage** - Decentralized, permanent storage
7. **Basic reputation** - Track record of completions and approvals
8. **Admin dispute resolution** - Manual mediation for conflicts

## Revenue Model

1. **Platform fees** - 10% of task budgets
2. **Artifact licensing** - 20% of artifact sales (80% to contributors)
3. **Premium features** - Priority matching, enhanced AI tools (future)

## Technical Approach

- **Frontend**: React PWA for mobile-first experience
- **Backend**: FastAPI (Python) for AI integrations
- **Blockchain**: Base (Ethereum L2) for low fees
- **Payment token**: cNGN (Nigerian Naira stablecoin)
- **Storage**: IPFS via Pinata for artifacts
- **AI**: Claude API for task decomposition and assistance

## Key Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| cNGN not available on Base | Medium | Use mock token for MVP, swap when available |
| Worker quality inconsistent | High | Start with verified workers, reputation gates |
| AI hallucinations in outputs | Medium | Human verification required for all AI content |
| Regulatory concerns | Low | Focus on research tasks, not financial services |
| Smart contract bugs | Medium | Comprehensive testing, start with small amounts |

## Success Metrics (MVP)

- 50+ verified workers onboarded
- 10+ tasks completed end-to-end
- 3+ artifacts created and listed
- <24hr average subtask completion
- >80% first-submission approval rate

## Open Questions

1. How to bootstrap initial supply of workers?
2. What's the right pricing model for tasks?
3. Should artifacts be NFTs or just registered hashes?
4. How to handle partial work and abandoned tasks?
5. What reputation decay model prevents gaming?

## Next Steps

1. Complete MVP implementation
2. Deploy to Base Sepolia testnet
3. Onboard pilot cohort of 20 workers
4. Run 5 test tasks with real clients
5. Iterate based on feedback

---

*This brainstorm captures the vision for Flow as of January 2025. The platform is currently in active development with Phase 1 (Foundation) complete and Phase 2 (Core Backend) in progress.*
