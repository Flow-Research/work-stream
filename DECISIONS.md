# Flow MVP - Technical Decisions

This document tracks key decisions made during development.

## Architecture Decisions

### D001: Vite over Expo Web
**Date**: 2025-01-06
**Decision**: Use Vite + React instead of Expo for Web
**Rationale**: 
- Simpler setup for web-first PWA
- Better wagmi/viem integration
- No React Native overhead for web-only MVP
- Can add React Native later if needed

### D002: Mock ERC20 Token for Testing
**Date**: 2025-01-06
**Decision**: Create MockCNGN ERC20 token for testnet
**Rationale**:
- cNGN availability on Base uncertain
- Need working payment flow for MVP
- Easy to swap address when real token available

### D003: SQLAlchemy 2.0 with Async
**Date**: 2025-01-06
**Decision**: Use SQLAlchemy 2.0 async patterns
**Rationale**:
- Better performance with FastAPI
- Modern Python async/await patterns
- Future-proof for scaling

### D004: In-Memory Session Cache Initially
**Date**: 2025-01-06
**Decision**: Start without Redis, use in-memory cache
**Rationale**:
- Reduces deployment complexity for MVP
- Single server sufficient for 10 users
- Easy to add Redis later

### D005: Foundry for Smart Contracts
**Date**: 2025-01-06
**Decision**: Use Foundry instead of Hardhat
**Rationale**:
- Faster compilation
- Better testing (Solidity tests)
- Lower gas usage in deployment
- Spec recommendation

## Implementation Decisions

(To be added as development progresses)

## Deferred Features

1. **Algorithm-based matching** - Manual filtering sufficient for MVP
2. **Knowledge graph visualization** - JSON export only
3. **Automated royalty distribution** - Manual tracking for v1
4. **Peer review layer** - Client approval only
5. **Native mobile apps** - PWA sufficient
6. **Redis caching** - In-memory for MVP
