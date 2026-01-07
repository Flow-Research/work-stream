import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.models.task import Task
from app.models.subtask import Subtask
from app.models.user import User


@pytest.fixture
async def funded_task(db_session: AsyncSession, admin_user: User) -> Task:
    task = Task(
        title="Test Research Task",
        description="A task for testing subtask flows",
        research_question="What are the best practices?",
        total_budget_cngn=10000.00,
        client_id=admin_user.id,
        status="funded",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def open_subtask(db_session: AsyncSession, funded_task: Task) -> Subtask:
    subtask = Subtask(
        task_id=funded_task.id,
        title="Test Subtask",
        description="A subtask for testing",
        subtask_type="discovery",
        sequence_order=1,
        budget_allocation_percent=50.0,
        budget_cngn=5000.00,
        status="open",
    )
    db_session.add(subtask)
    await db_session.commit()
    await db_session.refresh(subtask)
    return subtask


@pytest.mark.asyncio
async def test_list_subtasks(client: AsyncClient, open_subtask: Subtask):
    response = await client.get("/api/subtasks")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_subtask(client: AsyncClient, open_subtask: Subtask):
    response = await client.get(f"/api/subtasks/{open_subtask.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(open_subtask.id)
    assert data["title"] == "Test Subtask"
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_get_subtask_not_found(client: AsyncClient):
    import uuid
    response = await client.get(f"/api/subtasks/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_claim_subtask(
    client: AsyncClient,
    auth_headers: dict,
    open_subtask: Subtask,
    test_user: User,
):
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/claim",
        headers=auth_headers,
        json={},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "claimed"
    assert data["claimed_by"] == str(test_user.id)


@pytest.mark.asyncio
async def test_claim_subtask_requires_auth(client: AsyncClient, open_subtask: Subtask):
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/claim",
        json={},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_claim_already_claimed_subtask(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/claim",
        headers=auth_headers,
        json={},
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_unclaim_subtask(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/unclaim",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"
    assert data["claimed_by"] is None


@pytest.mark.asyncio
async def test_unclaim_not_your_subtask(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    admin_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = admin_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/unclaim",
        headers=auth_headers,
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_submit_work(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    with patch("app.api.routes.subtasks.IPFSService") as mock_ipfs:
        mock_instance = AsyncMock()
        mock_instance.pin_file = AsyncMock(return_value="QmTestHash123")
        mock_ipfs.return_value = mock_instance
        
        response = await client.post(
            f"/api/subtasks/{open_subtask.id}/submit",
            headers=auth_headers,
            data={"content_summary": "Completed the research task with findings."},
        )
    
    assert response.status_code == 200
    data = response.json()
    # SubmissionResponse returns submission status, not subtask status
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_submit_work_with_file(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    with patch("app.api.routes.subtasks.IPFSService") as mock_ipfs:
        mock_instance = AsyncMock()
        mock_instance.pin_file = AsyncMock(return_value="QmTestFileHash456")
        mock_ipfs.return_value = mock_instance
        
        response = await client.post(
            f"/api/subtasks/{open_subtask.id}/submit",
            headers=auth_headers,
            data={"content_summary": "Research findings attached."},
            files={"artifact": ("results.json", b'{"data": "test"}', "application/json")},
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_submit_work_invalid_file_type(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/submit",
        headers=auth_headers,
        data={"content_summary": "Test submission"},
        files={"artifact": ("script.py", b'print("hello")', "text/x-python")},
    )
    
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_submit_work_not_claimed_by_you(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    admin_user: User,
):
    open_subtask.status = "claimed"
    open_subtask.claimed_by = admin_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/submit",
        headers=auth_headers,
        data={"content_summary": "My submission"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_approve_submission(
    client: AsyncClient,
    admin_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    funded_task: Task,
    test_user: User,
):
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/approve",
        headers=admin_headers,
        json={"review_notes": "Good work!"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_approve_requires_admin_or_client(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/approve",
        headers=auth_headers,
        json={},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reject_submission(
    client: AsyncClient,
    admin_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/reject",
        headers=admin_headers,
        json={"review_notes": "Needs more detail on methodology."},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_reject_requires_review_notes(
    client: AsyncClient,
    admin_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()
    
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/reject",
        headers=admin_headers,
        json={},
    )
    
    assert response.status_code == 422
