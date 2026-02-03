# Flow - Research Synthesis Platform

Flow enables knowledge workers to earn by contributing to AI-assisted academic research synthesis. Workers verify AI outputs, add expertise, and build artifacts (datasets, knowledge graphs) that generate recurring revenue through licensing.

## Quick Start

### Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 15+** - Database (can use Docker)
- **Docker & Docker Compose** - For local PostgreSQL (optional but recommended)
- **tmux** - For the development helper script (optional)
- **Foundry** - For smart contract development (optional)

### One-Command Development Setup

If you have all prerequisites installed, use the helper script:

```bash
# Clone with submodules (for smart contracts)
git clone --recurse-submodules <repository-url>
cd Flow

# Start PostgreSQL with Docker
docker-compose up -d

# Run the development servers (requires tmux)
./run_dev.sh
```

This starts both backend (http://localhost:8000) and frontend (http://localhost:5173) in a tmux session.

---

### Manual Setup

#### Database Setup (Choose One)

**Option A: Docker (Recommended)**
```bash
# Start PostgreSQL container
docker-compose up -d

# Verify it's running
docker ps  # Should show flow-postgres container
```

**Option B: Local PostgreSQL**
```bash
# Create database
createdb flow

# Or via psql
psql -c "CREATE DATABASE flow;"
```

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section)

# Run database migrations
alembic upgrade head

# (Optional) Seed sample data
python scripts/setup_db.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file (if not exists)
# Create .env with:
#   VITE_API_URL=http://localhost:8000/api
#   VITE_WALLETCONNECT_PROJECT_ID=your-project-id
#   VITE_BASE_SEPOLIA_RPC=https://base-sepolia-rpc.publicnode.com

# Start development server
npm run dev
```

#### Smart Contracts Setup

```bash
cd contracts

# Initialize git submodules (OpenZeppelin, forge-std)
git submodule update --init --recursive

# Install Foundry if not installed
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install dependencies (alternative to submodules)
forge install

# Run tests
forge test

# Copy environment file for deployment
cp .env.example .env
# Edit with your deployer private key

# Deploy to Base Sepolia
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
│   ├── scripts/           # Database seeding scripts
│   └── tests/             # Backend tests
├── contracts/             # Solidity smart contracts
│   ├── src/               # Contract source
│   ├── test/              # Contract tests
│   ├── script/            # Deployment scripts
│   └── lib/               # Dependencies (git submodules)
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── stores/        # Zustand stores
│   │   └── types/         # TypeScript types
│   └── public/            # Static assets
├── specs/                 # Feature specifications
├── qa/                    # QA test cases and reports
├── docker-compose.yml     # PostgreSQL for local dev
├── run_dev.sh             # Development server launcher
├── run_tests.sh           # Test runner script
├── PLAN.md                # Build plan
├── DECISIONS.md           # Technical decisions
├── CHANGELOG.md           # Version history
└── README.md              # This file
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
| `/api/skills` | GET | List all skills |
| `/api/admin/subtasks` | GET | Admin: List subtasks with filters |
| `/api/admin/subtasks/{id}` | PATCH | Admin: Update subtask status |
| `/api/artifacts` | POST | Create new artifact |
| `/api/artifacts/{id}` | GET | Get artifact details |

## Development Scripts

### `run_dev.sh` - Start All Servers

Launches both backend and frontend in a tmux session with split panes:

```bash
./run_dev.sh
```

**Features:**
- Automatically seeds database if empty
- Backend runs on http://localhost:8000 (API docs at /docs)
- Frontend runs on http://localhost:5173
- Clean shutdown with Ctrl+C

**tmux commands:**
- `Ctrl+B, D` - Detach (servers keep running)
- `tmux attach -t flow-dev` - Reattach to session
- `tmux kill-session -t flow-dev` - Stop all servers

### `run_tests.sh` - Run All Tests

Runs backend, frontend, and contract tests in sequence:

```bash
./run_tests.sh
```

---

## Running Tests

### All Tests

```bash
./run_tests.sh
```

### Backend Tests

```bash
cd backend
source venv/bin/activate
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
| `DATABASE_URL` | Yes | PostgreSQL connection string (must use `+asyncpg` driver) |
| `JWT_SECRET` | Yes | Secret key for JWT token signing (use a 256-bit key) |
| `BASE_RPC_URL` | Yes | Base chain RPC endpoint |
| `ESCROW_CONTRACT_ADDRESS` | No | Deployed FlowEscrow contract address |
| `REGISTRY_CONTRACT_ADDRESS` | No | Deployed FlowArtifactRegistry address |
| `CNGN_CONTRACT_ADDRESS` | No | MockCNGN token contract address |
| `ADMIN_WALLET` | No | Admin wallet address for verification |
| `ADMIN_PRIVATE_KEY` | No | Admin private key for signing contract transactions |
| `CLAUDE_API_KEY` | No | Anthropic API key for AI features |
| `PINATA_API_KEY` | No | Pinata API key for IPFS uploads |
| `PINATA_SECRET` | No | Pinata secret for IPFS uploads |
| `CORS_ORIGINS` | No | Allowed CORS origins (JSON array, defaults to localhost) |
| `DEBUG` | No | Enable debug mode (default: false) |

Example `.env` file:
```bash
# Application
DEBUG=true
APP_NAME="Flow API"

# Database (required)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/flow

# Security (required)
JWT_SECRET=your-256-bit-secret-key-change-in-production

# Blockchain
BASE_RPC_URL=https://sepolia.base.org
ESCROW_CONTRACT_ADDRESS=0xf10D75Bd61eA5071677aE209FD3a9aA334Ac14FF
REGISTRY_CONTRACT_ADDRESS=0x120ddd1Be4534d2Bd24009b913eB3057a2251751
CNGN_CONTRACT_ADDRESS=0xfdf794bfBC24bCc7aE733a33a78CE16e71024821
ADMIN_WALLET=0x...your-admin-wallet-address
ADMIN_PRIVATE_KEY=your-admin-private-key-for-payment-release

# External Services (optional - features degrade gracefully without these)
CLAUDE_API_KEY=your-anthropic-key
PINATA_API_KEY=your-pinata-key
PINATA_SECRET=your-pinata-secret

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### Frontend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API URL |
| `VITE_WALLETCONNECT_PROJECT_ID` | No | WalletConnect project ID for wallet connections |
| `VITE_BASE_SEPOLIA_RPC` | No | Base Sepolia RPC URL for direct chain reads |

```bash
VITE_API_URL=http://localhost:8000/api
VITE_WALLETCONNECT_PROJECT_ID=your-project-id
VITE_BASE_SEPOLIA_RPC=https://base-sepolia-rpc.publicnode.com
```

### Contracts (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_RPC_URL` | Yes | Base chain RPC endpoint |
| `PRIVATE_KEY` | Yes | Deployer wallet private key (needs Base Sepolia ETH) |
| `BASESCAN_API_KEY` | No | BaseScan API key for contract verification |

```bash
BASE_RPC_URL=https://sepolia.base.org
PRIVATE_KEY=your_deployer_private_key
BASESCAN_API_KEY=your_basescan_api_key  # Optional, for verification
```

Get testnet ETH from: https://www.coinbase.com/faucets/base-sepolia-faucet

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

### Docker/PostgreSQL issues
- Ensure Docker is running: `docker ps`
- Start database: `docker-compose up -d`
- Check container logs: `docker logs flow-postgres`
- Reset database: `docker-compose down -v && docker-compose up -d`

### Database connection issues
- Ensure PostgreSQL is running: `pg_isready` or `docker ps`
- Check DATABASE_URL format includes `+asyncpg`
- Verify database exists: `psql -l | grep flow`

### tmux/run_dev.sh issues
- Install tmux: `brew install tmux` (macOS) or `apt install tmux` (Ubuntu)
- Kill stuck session: `tmux kill-session -t flow-dev`
- Run servers manually if tmux unavailable (see Manual Setup)

### Contract interaction fails
- Verify contract addresses in .env match deployed contracts
- Ensure wallet has sufficient ETH for gas
- Check you're on Base Sepolia network, not mainnet

### Git submodules missing (contracts)
- Run: `git submodule update --init --recursive`
- Or reinstall: `cd contracts && forge install`

### IPFS uploads fail
- Verify Pinata credentials are set
- Without credentials, uploads return mock hashes (dev only)

### Authentication errors
- Clear browser localStorage and reconnect wallet
- Ensure wallet is connected to Base Sepolia network
- Check JWT_SECRET is set in backend .env

### AI features not working
- Verify CLAUDE_API_KEY is set in backend .env
- Check API key has sufficient credits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
