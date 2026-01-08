# Flow - Decentralized Research Synthesis Platform

Flow enables knowledge workers to earn by contributing to AI-assisted academic research synthesis. Workers verify AI outputs, add expertise, and build artifacts (datasets, knowledge graphs) that generate recurring revenue through licensing.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Foundry (for smart contracts)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Smart Contracts Setup

```bash
cd contracts

# Install Foundry if not installed
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install dependencies
forge install

# Run tests
forge test

# Deploy to Base Sepolia (requires PRIVATE_KEY and FEE_RECIPIENT env vars)
forge script script/Deploy.s.sol --rpc-url https://sepolia.base.org --broadcast
```

## Project Structure

```
Flow/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, security
│   │   ├── db/            # Database setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # App entry point
│   ├── alembic/           # Database migrations
│   └── tests/             # Backend tests
├── contracts/             # Solidity smart contracts
│   ├── src/               # Contract source
│   ├── test/              # Contract tests
│   └── script/            # Deployment scripts
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── stores/        # Zustand stores
│   │   └── types/         # TypeScript types
│   └── public/            # Static assets
├── PLAN.md               # Build plan
├── DECISIONS.md          # Technical decisions
└── README.md             # This file
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/nonce` | POST | Get nonce for wallet auth |
| `/api/auth/verify` | POST | Verify wallet signature |
| `/api/users/me` | GET | Get current user profile |
| `/api/tasks` | GET | List all tasks |
| `/api/tasks/{id}` | GET | Get task details |
| `/api/subtasks/{id}/claim` | POST | Claim a subtask |
| `/api/subtasks/{id}/submit` | POST | Submit work |
| `/api/ai/decompose-task` | POST | AI task decomposition |

## Running Tests

### Backend Tests

```bash
cd backend
pytest -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Contract Tests

```bash
cd contracts
forge test -vvv
```

## Environment Variables

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (asyncpg) |
| `JWT_SECRET` | Yes | Secret key for JWT token signing (256-bit) |
| `BASE_RPC_URL` | Yes | Base chain RPC endpoint |
| `ESCROW_CONTRACT_ADDRESS` | Yes | Deployed FlowEscrow contract address |
| `REGISTRY_CONTRACT_ADDRESS` | Yes | Deployed FlowArtifactRegistry address |
| `CNGN_CONTRACT_ADDRESS` | Yes | MockCNGN token contract address |
| `CLAUDE_API_KEY` | No | Anthropic API key for AI features |
| `PINATA_API_KEY` | No | Pinata API key for IPFS uploads |
| `PINATA_SECRET` | No | Pinata secret for IPFS uploads |

Example `.env` file:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/flow
JWT_SECRET=your-256-bit-secret-key-change-in-production
BASE_RPC_URL=https://sepolia.base.org
ESCROW_CONTRACT_ADDRESS=0xf10D75Bd61eA5071677aE209FD3a9aA334Ac14FF
REGISTRY_CONTRACT_ADDRESS=0x120ddd1Be4534d2Bd24009b913eB3057a2251751
CNGN_CONTRACT_ADDRESS=0xfdf794bfBC24bCc7aE733a33a78CE16e71024821
CLAUDE_API_KEY=your-anthropic-key
PINATA_API_KEY=your-pinata-key
PINATA_SECRET=your-pinata-secret
```

### Frontend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API URL |
| `VITE_WALLETCONNECT_PROJECT_ID` | No | WalletConnect project ID |

```
VITE_API_URL=http://localhost:8000/api
VITE_WALLETCONNECT_PROJECT_ID=your-project-id
```

## Deployed Contracts (Base Sepolia)

| Contract | Address |
|----------|---------|
| MockCNGN | `0xfdf794bfBC24bCc7aE733a33a78CE16e71024821` |
| FlowEscrow | `0xf10D75Bd61eA5071677aE209FD3a9aA334Ac14FF` |
| FlowArtifactRegistry | `0x120ddd1Be4534d2Bd24009b913eB3057a2251751` |

## Smart Contracts

### FlowEscrow

Handles task payment escrow:
- `fundTask(amount)` - Create escrow for a task
- `approveSubtask(taskId, index, worker, amount)` - Release payment
- `completeTask(taskId)` - Complete and refund remainder
- `raiseDispute(taskId)` - Freeze funds for dispute
- `resolveDispute(taskId, winner, amount)` - Admin resolution

### FlowArtifactRegistry

On-chain artifact provenance:
- `registerArtifact(id, contentHash, contributors)` - Register artifact
- `getArtifact(id)` - Get artifact details
- `verifyArtifact(id, hash)` - Verify content hash

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   React Frontend    │────▶│   FastAPI Backend   │
│   (Vite + wagmi)    │     │   (Python 3.11)     │
└─────────────────────┘     └──────────┬──────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌─────────────────┐           ┌─────────────────┐
│  PostgreSQL   │            │   Base Chain    │           │      IPFS       │
│   Database    │            │  (Smart Contr)  │           │   (Pinata)      │
└───────────────┘            └─────────────────┘           └─────────────────┘
```

## Deployment

### Backend (Railway)

1. Connect GitHub repository
2. Set environment variables
3. Deploy with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Connect GitHub repository
2. Set `VITE_API_URL` environment variable
3. Deploy automatically

### Contracts (Base Mainnet)

1. Set `PRIVATE_KEY` and `FEE_RECIPIENT`
2. Run: `forge script script/Deploy.s.sol --rpc-url https://mainnet.base.org --broadcast --verify`

## Rate Limiting

The API implements rate limiting on sensitive endpoints:
- AI endpoints: 10 requests/minute per IP
- Auth endpoints: 5 requests/minute per IP

Rate limit headers are returned with each response.

## Database Migrations

This project uses Alembic for database migrations:

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Troubleshooting

### Database connection issues
- Ensure PostgreSQL is running: `pg_isready`
- Check DATABASE_URL format includes `+asyncpg`

### Contract interaction fails
- Verify contract addresses in .env match deployed contracts
- Ensure wallet has sufficient ETH for gas

### IPFS uploads fail
- Verify Pinata credentials are set
- Without credentials, uploads return mock hashes (dev only)

### Authentication errors
- Clear browser localStorage and reconnect wallet
- Ensure wallet is connected to Base Sepolia network

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
