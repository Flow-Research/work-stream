# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-06

### Added
- Initial project structure with FastAPI backend, React frontend, and Solidity smart contracts
- User model with wallet-based authentication (nonce + signature verification)
- Task and Subtask models with full lifecycle support
- Submission and Artifact models for work output tracking
- Dispute model for conflict resolution
- FlowEscrow smart contract for payment escrow management
- FlowArtifactRegistry smart contract for on-chain artifact registration
- MockCNGN ERC20 token for testnet development
- AI service integration with Claude API for task decomposition
- IPFS service integration via Pinata for artifact storage
- Semantic Scholar integration for paper discovery
- Docker Compose setup for PostgreSQL
- Development scripts (run_dev.sh, run_tests.sh, setup_db.py)
- Comprehensive API documentation in specs folder
