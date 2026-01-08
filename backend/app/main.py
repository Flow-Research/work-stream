from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routes import auth, users, tasks, subtasks, ai, artifacts, admin
from app.core.config import settings
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting Flow API...")
    yield
    # Shutdown
    print("Shutting down Flow API...")


app = FastAPI(
    title=settings.app_name,
    description="Decentralized research synthesis platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["users"])
app.include_router(tasks.router, prefix=f"{settings.api_v1_prefix}/tasks", tags=["tasks"])
app.include_router(subtasks.router, prefix=f"{settings.api_v1_prefix}/subtasks", tags=["subtasks"])
app.include_router(ai.router, prefix=f"{settings.api_v1_prefix}/ai", tags=["ai"])
app.include_router(artifacts.router, prefix=f"{settings.api_v1_prefix}/artifacts", tags=["artifacts"])
app.include_router(admin.router, prefix=f"{settings.api_v1_prefix}/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Flow API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
