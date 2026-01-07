#!/bin/bash

trap 'kill $(jobs -p) 2>/dev/null; exit' INT TERM

echo "=== Starting Flow Development Servers ==="

cd "$(dirname "$0")"

echo ""
echo "Starting PostgreSQL..."
docker compose up -d postgres
sleep 2

echo ""
echo "Setting up database..."
cd backend
source venv/bin/activate
python scripts/setup_db.py

echo ""
echo "Starting backend on http://localhost:8000 ..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

echo ""
echo "Starting frontend on http://localhost:5173 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== Both servers running ==="
echo "Backend:  http://localhost:8000 (API docs: http://localhost:8000/docs)"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

wait
