"""Test configuration and fixtures."""
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token

try:
    from testcontainers.postgres import PostgresContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False

DOCKER_AVAILABLE = False
_postgres_container = None


def _check_docker():
    global DOCKER_AVAILABLE, _postgres_container
    
    if not TESTCONTAINERS_AVAILABLE:
        return False
    
    if os.getenv("SKIP_DOCKER_TESTS", "").lower() in ("1", "true", "yes"):
        return False
    
    try:
        _postgres_container = PostgresContainer(
            image="postgres:15-alpine",
            username="test",
            password="test",
            dbname="flow_test",
        )
        _postgres_container.start()
        DOCKER_AVAILABLE = True
        return True
    except Exception as e:
        print(f"Docker not available: {e}")
        DOCKER_AVAILABLE = False
        return False


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database connection"
    )
    _check_docker()


def pytest_unconfigure(config):
    global _postgres_container
    if _postgres_container is not None:
        try:
            _postgres_container.stop()
        except Exception:
            pass


def pytest_collection_modifyitems(config, items):
    if DOCKER_AVAILABLE:
        return
    
    skip_db = pytest.mark.skip(
        reason="Docker not available - install Docker to run integration tests"
    )
    for item in items:
        if "requires_db" in item.keywords or "integration" in str(item.fspath):
            item.add_marker(skip_db)


@pytest.fixture(scope="session")
def database_url() -> str:
    if DOCKER_AVAILABLE and _postgres_container is not None:
        host = _postgres_container.get_container_host_ip()
        port = _postgres_container.get_exposed_port(5432)
        return f"postgresql+asyncpg://test:test@{host}:{port}/flow_test"
    
    return os.getenv(
        "TEST_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/flow_test")
    )


_tables_created = False


@pytest_asyncio.fixture
async def db_session(database_url: str) -> AsyncGenerator[AsyncSession, None]:
    global _tables_created
    
    engine = create_async_engine(database_url, echo=False)
    
    try:
        if not _tables_created:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _tables_created = True
        
        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        async with session_factory() as session:
            yield session
        
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        wallet_address="0x1234567890123456789012345678901234567890",
        name="Test User",
        country="NG",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        wallet_address="0x0987654321098765432109876543210987654321",
        name="Admin User",
        country="NG",
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user: User) -> dict:
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}
