"""Integration tests for task endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User


@pytest.mark.asyncio
async def test_list_tasks_empty(client: AsyncClient):
    """Test listing tasks when none exist."""
    response = await client.get("/api/tasks")
    
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_task_requires_admin(client: AsyncClient, auth_headers: dict):
    """Test that creating tasks requires admin."""
    response = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={
            "title": "Test Task",
            "description": "Test description",
            "research_question": "What is the test?",
            "total_budget_cngn": "1000.00",
        },
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_task_as_admin(client: AsyncClient, admin_headers: dict):
    """Test creating a task as admin."""
    response = await client.post(
        "/api/tasks",
        headers=admin_headers,
        json={
            "title": "Test Research Task",
            "description": "A test research task",
            "research_question": "What are the failure modes of LLMs?",
            "total_budget_cngn": "5000.00",
            "skills_required": ["research", "nlp"],
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Research Task"
    assert data["status"] == "draft"
    assert float(data["total_budget_cngn"]) == 5000.00


@pytest.mark.asyncio
async def test_get_task(
    client: AsyncClient,
    db_session: AsyncSession,
    admin_user: User,
):
    """Test getting a specific task."""
    # Create task directly
    task = Task(
        title="Test Task",
        description="Description",
        research_question="Question?",
        total_budget_cngn=1000.00,
        client_id=admin_user.id,
        status="draft",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    
    response = await client.get(f"/api/tasks/{task.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"


@pytest.mark.asyncio
async def test_get_task_not_found(client: AsyncClient):
    """Test getting a non-existent task."""
    import uuid
    
    response = await client.get(f"/api/tasks/{uuid.uuid4()}")
    
    assert response.status_code == 404
