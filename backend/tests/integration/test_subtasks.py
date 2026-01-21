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


# =====================================================
# Dispute Tests
# =====================================================


@pytest.mark.asyncio
async def test_create_dispute_as_worker(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    """Worker who claimed the subtask can create a dispute."""
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()

    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/dispute",
        headers=auth_headers,
        json={"reason": "The review feedback was unfair and does not address the actual deliverables."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"
    assert data["raised_by"] == str(test_user.id)
    assert data["subtask_id"] == str(open_subtask.id)


@pytest.mark.asyncio
async def test_create_dispute_as_client(
    client: AsyncClient,
    admin_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    funded_task: Task,
    test_user: User,
):
    """Task client (admin in this case) can create a dispute."""
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()

    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/dispute",
        headers=admin_headers,
        json={"reason": "The submitted work does not meet the quality standards specified."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_create_dispute_updates_subtask_status(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    """Creating a dispute updates the subtask status to 'disputed'."""
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()

    await client.post(
        f"/api/subtasks/{open_subtask.id}/dispute",
        headers=auth_headers,
        json={"reason": "The review feedback was unfair and incorrect."},
    )

    # Fetch the subtask to verify status update
    response = await client.get(f"/api/subtasks/{open_subtask.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "disputed"


@pytest.mark.asyncio
async def test_create_dispute_requires_auth(
    client: AsyncClient,
    open_subtask: Subtask,
):
    """Unauthenticated users cannot create disputes."""
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/dispute",
        json={"reason": "This is a valid dispute reason that is long enough."},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_dispute_not_authorized(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    admin_user: User,
):
    """User who is not involved in the subtask cannot dispute."""
    # Set up subtask claimed by admin, not test_user
    open_subtask.status = "submitted"
    open_subtask.claimed_by = admin_user.id
    await db_session.commit()

    # test_user (via auth_headers) tries to dispute
    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/dispute",
        headers=auth_headers,
        json={"reason": "I want to dispute this even though I'm not involved."},
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_dispute_reason_too_short(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    """Dispute reason must be at least 10 characters."""
    open_subtask.status = "submitted"
    open_subtask.claimed_by = test_user.id
    await db_session.commit()

    response = await client.post(
        f"/api/subtasks/{open_subtask.id}/dispute",
        headers=auth_headers,
        json={"reason": "Short"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_dispute_subtask_not_found(
    client: AsyncClient,
    auth_headers: dict,
):
    """Dispute on non-existent subtask returns 404."""
    import uuid
    response = await client.post(
        f"/api/subtasks/{uuid.uuid4()}/dispute",
        headers=auth_headers,
        json={"reason": "This is a valid dispute reason for a non-existent subtask."},
    )

    assert response.status_code == 404


# =====================================================
# End-to-End Flow Tests
# =====================================================


@pytest.mark.asyncio
async def test_full_subtask_flow_claim_submit_approve(
    client: AsyncClient,
    auth_headers: dict,
    admin_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    """Test the complete happy path: claim → submit → approve."""
    # Step 1: Claim the subtask
    claim_response = await client.post(
        f"/api/subtasks/{open_subtask.id}/claim",
        headers=auth_headers,
        json={},
    )
    assert claim_response.status_code == 200
    assert claim_response.json()["status"] == "claimed"

    # Step 2: Submit work
    with patch("app.api.routes.subtasks.IPFSService") as mock_ipfs:
        mock_instance = AsyncMock()
        mock_instance.pin_file = AsyncMock(return_value="QmFlowTestHash789")
        mock_ipfs.return_value = mock_instance

        submit_response = await client.post(
            f"/api/subtasks/{open_subtask.id}/submit",
            headers=auth_headers,
            data={"content_summary": "Completed research with comprehensive findings."},
            files={"artifact": ("research.json", b'{"findings": "test data"}', "application/json")},
        )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == "pending"

    # Step 3: Approve the submission
    approve_response = await client.post(
        f"/api/subtasks/{open_subtask.id}/approve",
        headers=admin_headers,
        json={"review_notes": "Excellent work, meets all requirements."},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_full_subtask_flow_claim_submit_reject_resubmit(
    client: AsyncClient,
    auth_headers: dict,
    admin_headers: dict,
    db_session: AsyncSession,
    open_subtask: Subtask,
    test_user: User,
):
    """Test rejection flow: claim → submit → reject → resubmit."""
    # Step 1: Claim
    await client.post(
        f"/api/subtasks/{open_subtask.id}/claim",
        headers=auth_headers,
        json={},
    )

    # Step 2: Submit (first attempt)
    with patch("app.api.routes.subtasks.IPFSService") as mock_ipfs:
        mock_instance = AsyncMock()
        mock_instance.pin_file = AsyncMock(return_value="QmFirstAttempt")
        mock_ipfs.return_value = mock_instance

        await client.post(
            f"/api/subtasks/{open_subtask.id}/submit",
            headers=auth_headers,
            data={"content_summary": "Initial submission."},
        )

    # Step 3: Reject
    reject_response = await client.post(
        f"/api/subtasks/{open_subtask.id}/reject",
        headers=admin_headers,
        json={"review_notes": "Please add more detail to the methodology section."},
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"

    # Step 4: Resubmit (after rejection, subtask goes back to claimed)
    # First update status to claimed to allow resubmission
    await db_session.refresh(open_subtask)
    open_subtask.status = "claimed"
    await db_session.commit()

    with patch("app.api.routes.subtasks.IPFSService") as mock_ipfs:
        mock_instance = AsyncMock()
        mock_instance.pin_file = AsyncMock(return_value="QmSecondAttempt")
        mock_ipfs.return_value = mock_instance

        resubmit_response = await client.post(
            f"/api/subtasks/{open_subtask.id}/submit",
            headers=auth_headers,
            data={"content_summary": "Improved submission with detailed methodology."},
        )
    assert resubmit_response.status_code == 200
