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

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/flow
JWT_SECRET=your-secret-key
BASE_RPC_URL=https://sepolia.base.org
ESCROW_CONTRACT_ADDRESS=0x...
REGISTRY_CONTRACT_ADDRESS=0x...
CLAUDE_API_KEY=your-anthropic-key
PINATA_API_KEY=your-pinata-key
PINATA_SECRET=your-pinata-secret
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000/api
VITE_WALLETCONNECT_PROJECT_ID=your-project-id
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
