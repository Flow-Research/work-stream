#!/bin/bash

SESSION="flow-dev"
SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if running in terminal
if [ ! -t 1 ]; then
    echo "Error: This script must be run in an interactive terminal."
    echo "Run it directly in your terminal: ./run_dev.sh"
    exit 1
fi

# Cleanup tmux session on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    tmux kill-session -t $SESSION 2>/dev/null
    # Kill background processes
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo "Servers stopped."
}

trap cleanup INT TERM EXIT

echo "=== Starting Flow Development Servers ==="

cd "$SESSION_DIR"

# Skip Docker postgres (using fitstudio-db)
echo "Using existing PostgreSQL on port 5432 (fitstudio-db)"

# Setup database (only if data doesn't exist)
echo "Setting up database..."
cd backend
source venv/bin/activate
# Check if users table exists and has data
if python -c "import asyncio; from app.db.session import async_session; from sqlalchemy import text; asyncio.run(async_session().__aenter__()); async with async_session() as s: await s.execute(text('SELECT 1 FROM users LIMIT 1')); print('OK')" 2>/dev/null; then
    echo "Database already initialized."
else
    echo "Seeding database..."
    python scripts/setup_db.py
fi
cd ..

# Kill existing tmux session if running
tmux kill-session -t $SESSION 2>/dev/null

# Create new tmux session
echo ""
echo "Starting servers in tmux session: $SESSION"
echo ""
echo "Backend:  http://localhost:8000 (API docs: http://localhost:8000/docs)"
echo "Frontend: http://localhost:5173"
echo ""
echo "=== Tmux Commands ==="
echo "  Ctrl+B, D       : Detach (servers keep running)"
echo "  tmux attach -t $SESSION : Reattach to session"
echo "  Ctrl+C in pane     : Kill server in that pane"
echo ""
echo "Use 'tmux kill-session -t $SESSION' to stop all servers from another terminal"
echo ""

# Create tmux session with vertical split (backend top, frontend bottom)
tmux new-session -d -s $SESSION -n "Flow Dev" -c "$SESSION_DIR/backend"

# Backend (top pane)
tmux send-keys -t $SESSION:0.0 "source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" C-m

# Split pane for frontend (bottom pane)
tmux split-window -v -t $SESSION -c "$SESSION_DIR/frontend"
tmux send-keys -t $SESSION:0.1 "npm run dev" C-m
tmux select-pane -t $SESSION:0.0

# Attach to tmux session
tmux attach -t $SESSION
