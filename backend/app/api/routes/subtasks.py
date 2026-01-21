"""Subtask endpoints."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DbSession, AdminUser
from app.models.subtask import Subtask
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.schemas.subtask import (
    SubtaskClaimRequest,
    SubtaskCreate,
    SubtaskListResponse,
    SubtaskRejectRequest,
    SubtaskResponse,
    SubtaskUpdate,
)
from app.schemas.submission import SubmissionResponse
from app.schemas.dispute import DisputeCreate, DisputeResponse
from app.models.dispute import Dispute
from app.services.ipfs import IPFSService
from app.services.blockchain import BlockchainService

# Constants for file validation
ALLOWED_FILE_EXTENSIONS = {"json", "csv", "md", "txt"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

router = APIRouter()


@router.get("", response_model=SubtaskListResponse)
async def list_subtasks(
    db: DbSession,
    status_filter: Optional[str] = Query(None, alias="status"),
    task_id: Optional[UUID] = Query(None),
    skills: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> SubtaskListResponse:
    """
    List subtasks with optional filtering.
    
    Args:
        db: Database session
        status_filter: Filter by subtask status
        task_id: Filter by parent task
        skills: Filter by skills (from parent task)
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated list of subtasks
    """
    query = select(Subtask)
    count_query = select(func.count(Subtask.id))
    
    if status_filter:
        query = query.where(Subtask.status == status_filter)
        count_query = count_query.where(Subtask.status == status_filter)
    
    if task_id:
        query = query.where(Subtask.task_id == task_id)
        count_query = count_query.where(Subtask.task_id == task_id)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Subtask.created_at.desc())
    
    result = await db.execute(query)
    subtasks = result.scalars().all()
    
    return SubtaskListResponse(
        subtasks=[SubtaskResponse.model_validate(st) for st in subtasks],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{subtask_id}", response_model=SubtaskResponse)
async def get_subtask(
    subtask_id: UUID,
    db: DbSession,
) -> SubtaskResponse:
    """
    Get a specific subtask.
    
    Args:
        subtask_id: The subtask ID
        db: Database session
        
    Returns:
        The subtask data
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )
    
    return SubtaskResponse.model_validate(subtask)


@router.post("/{subtask_id}/claim", response_model=SubtaskResponse)
async def claim_subtask(
    subtask_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    claim_request: Optional[SubtaskClaimRequest] = None,
) -> SubtaskResponse:
    """
    Claim a subtask for work.
    
    Args:
        subtask_id: The subtask ID
        claim_request: Optional collaborators and splits
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The claimed subtask
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )
    
    if subtask.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask is not available for claiming",
        )
    
    # Check task is in proper state
    task_result = await db.execute(select(Task).where(Task.id == subtask.task_id))
    task = task_result.scalar_one_or_none()
    
    if task is None or task.status not in ("funded", "decomposed", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not available for work",
        )
    
    # Handle collaborators
    collaborator_ids = None
    collaborator_splits = None
    
    if claim_request and claim_request.collaborators:
        # Validate collaborators exist
        collaborator_ids = []
        for wallet in claim_request.collaborators:
            user_result = await db.execute(
                select(User).where(User.wallet_address == wallet.lower())
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Collaborator not found: {wallet}",
                )
            collaborator_ids.append(user.id)
        
        if claim_request.splits:
            if len(claim_request.splits) != len(claim_request.collaborators) + 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Splits must include claimer and all collaborators",
                )
            if sum(claim_request.splits) != Decimal("100"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Splits must sum to 100",
                )
            collaborator_splits = claim_request.splits[1:]  # First is claimer's split
    
    subtask.status = "claimed"
    subtask.claimed_by = current_user.id
    subtask.claimed_at = datetime.utcnow()
    subtask.collaborators = collaborator_ids
    subtask.collaborator_splits = collaborator_splits
    
    # Update task status if first claim
    if task.status in ("funded", "decomposed"):
        task.status = "in_progress"
    
    await db.flush()
    await db.refresh(subtask)
    
    return SubtaskResponse.model_validate(subtask)


@router.post("/{subtask_id}/unclaim", response_model=SubtaskResponse)
async def unclaim_subtask(
    subtask_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> SubtaskResponse:
    """
    Unclaim a subtask.
    
    Args:
        subtask_id: The subtask ID
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The unclaimed subtask
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )
    
    if subtask.claimed_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to unclaim this subtask",
        )
    
    if subtask.status not in ("claimed", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unclaim subtask in current status",
        )
    
    subtask.status = "open"
    subtask.claimed_by = None
    subtask.claimed_at = None
    subtask.collaborators = None
    subtask.collaborator_splits = None
    
    await db.flush()
    await db.refresh(subtask)
    
    return SubtaskResponse.model_validate(subtask)


@router.post("/{subtask_id}/submit", response_model=SubmissionResponse)
async def submit_work(
    subtask_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    content_summary: str = Form(...),
    artifact: Optional[UploadFile] = File(None),
) -> SubmissionResponse:
    """
    Submit work for a subtask.
    
    Args:
        subtask_id: The subtask ID
        content_summary: Summary of the work
        artifact: Optional artifact file
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The submission
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )
    
    if subtask.claimed_by != current_user.id:
        # Check if user is a collaborator
        is_collaborator = (
            subtask.collaborators and current_user.id in subtask.collaborators
        )
        if not is_collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to submit for this subtask",
            )
    
    if subtask.status not in ("claimed", "in_progress", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit for subtask in current status",
        )
    
    artifact_ipfs_hash = None
    artifact_type = None
    
    if artifact:
        if not artifact.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Artifact filename is required",
            )
        
        file_ext = artifact.filename.split(".")[-1].lower() if "." in artifact.filename else ""
        if file_ext not in ALLOWED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}",
            )
        
        file_content = await artifact.read()
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed ({MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB)",
            )
        
        ipfs_service = IPFSService()
        try:
            artifact_ipfs_hash = await ipfs_service.pin_file(file_content, artifact.filename)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to upload artifact to IPFS: {str(e)}",
            )
        
        artifact_type = file_ext
    
    # Create submission
    submission = Submission(
        subtask_id=subtask_id,
        submitted_by=current_user.id,
        content_summary=content_summary,
        artifact_ipfs_hash=artifact_ipfs_hash,
        artifact_type=artifact_type,
        status="pending",
    )
    db.add(submission)
    
    # Update subtask status
    subtask.status = "submitted"
    subtask.submitted_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(submission)
    
    return SubmissionResponse.model_validate(submission)


@router.post("/{subtask_id}/approve", response_model=SubtaskResponse)
async def approve_subtask(
    subtask_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    review_notes: Optional[str] = None,
) -> SubtaskResponse:
    """
    Approve a submitted subtask and release payment to the worker.

    This endpoint:
    1. Validates the subtask is in submitted status
    2. Calls the smart contract to release payment
    3. Updates the database with approval status and tx hash

    Args:
        subtask_id: The subtask ID
        review_notes: Optional review notes
        current_user: The authenticated user (must be client or admin)
        db: Database session

    Returns:
        The approved subtask
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()

    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )

    # Get parent task to check authorization
    task_result = await db.execute(select(Task).where(Task.id == subtask.task_id))
    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve this subtask",
        )

    if subtask.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask is not pending approval",
        )

    # Get the latest submission
    sub_result = await db.execute(
        select(Submission)
        .where(Submission.subtask_id == subtask_id)
        .order_by(Submission.created_at.desc())
        .limit(1)
    )
    submission = sub_result.scalar_one_or_none()

    # Get worker info for payment
    worker = None
    if subtask.claimed_by:
        worker_result = await db.execute(
            select(User).where(User.id == subtask.claimed_by)
        )
        worker = worker_result.scalar_one_or_none()

    # Attempt blockchain payment release
    payment_tx_hash = None
    if worker and task.escrow_contract_task_id is not None and subtask.budget_cngn:
        blockchain_service = BlockchainService()

        if blockchain_service.is_configured():
            # Calculate payment amount in wei (18 decimals)
            payment_amount_wei = int(Decimal(str(subtask.budget_cngn)) * Decimal("1e18"))

            # Get subtask index within the task
            subtask_index_result = await db.execute(
                select(func.count(Subtask.id))
                .where(Subtask.task_id == task.id)
                .where(Subtask.sequence_order < subtask.sequence_order)
            )
            subtask_index = subtask_index_result.scalar_one() or 0

            try:
                payment_tx_hash = await blockchain_service.approve_subtask_payment(
                    task_id=task.escrow_contract_task_id,
                    subtask_index=subtask_index,
                    worker_address=worker.wallet_address,
                    amount_wei=payment_amount_wei,
                )
            except Exception as e:
                # Log error but don't fail the approval
                print(f"Blockchain payment failed: {e}")

    # Update submission
    if submission:
        submission.status = "approved"
        submission.reviewed_by = current_user.id
        submission.reviewed_at = datetime.utcnow()
        submission.review_notes = review_notes
        if payment_tx_hash:
            submission.payment_tx_hash = payment_tx_hash

    subtask.status = "approved"
    subtask.approved_at = datetime.utcnow()
    subtask.approved_by = current_user.id

    # Update worker reputation
    if worker:
        worker.tasks_completed += 1
        worker.tasks_approved += 1

    await db.flush()
    await db.refresh(subtask)

    return SubtaskResponse.model_validate(subtask)


@router.post("/{subtask_id}/reject", response_model=SubtaskResponse)
async def reject_subtask(
    subtask_id: UUID,
    reject_data: SubtaskRejectRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> SubtaskResponse:
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )
    
    # Get parent task to check authorization
    task_result = await db.execute(select(Task).where(Task.id == subtask.task_id))
    task = task_result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this subtask",
        )
    
    if subtask.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask is not pending review",
        )
    
    # Update submission
    sub_result = await db.execute(
        select(Submission)
        .where(Submission.subtask_id == subtask_id)
        .order_by(Submission.created_at.desc())
        .limit(1)
    )
    submission = sub_result.scalar_one_or_none()
    
    if submission:
        submission.status = "rejected"
        submission.reviewed_by = current_user.id
        submission.reviewed_at = datetime.utcnow()
        submission.review_notes = reject_data.review_notes
    
    subtask.status = "rejected"
    
    await db.flush()
    await db.refresh(subtask)
    
    return SubtaskResponse.model_validate(subtask)


@router.post("/{subtask_id}/dispute", response_model=DisputeResponse)
async def create_dispute(
    subtask_id: UUID,
    dispute_data: DisputeCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> DisputeResponse:
    """
    Create a dispute for a subtask.

    Args:
        subtask_id: The subtask ID
        dispute_data: The dispute reason
        current_user: The authenticated user
        db: Database session

    Returns:
        The created dispute
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()

    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )

    # Check user is involved (worker or client)
    task_result = await db.execute(select(Task).where(Task.id == subtask.task_id))
    task = task_result.scalar_one_or_none()

    is_client = task and task.client_id == current_user.id
    is_worker = subtask.claimed_by == current_user.id
    is_collaborator = subtask.collaborators and current_user.id in subtask.collaborators

    if not (is_client or is_worker or is_collaborator or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to dispute this subtask",
        )

    dispute = Dispute(
        subtask_id=subtask_id,
        raised_by=current_user.id,
        reason=dispute_data.reason,
        status="open",
    )
    db.add(dispute)

    subtask.status = "disputed"
    if task:
        task.status = "disputed"

    await db.flush()
    await db.refresh(dispute)

    return DisputeResponse.model_validate(dispute)


# ============ Admin/Client CRUD Endpoints ============

@router.post("", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    subtask_data: SubtaskCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> SubtaskResponse:
    """
    Create a new subtask for a task.
    Only the task owner or admin can create subtasks.

    Args:
        subtask_data: The subtask data
        db: Database session
        current_user: The authenticated user

    Returns:
        The created subtask
    """
    # Get the parent task
    task_result = await db.execute(select(Task).where(Task.id == subtask_data.task_id))
    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check authorization - only task owner or admin
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add subtasks to this task",
        )

    # Validate task status - can only add subtasks to draft, funded, or decomposed tasks
    if task.status not in ("draft", "funded", "decomposed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add subtasks to task in current status",
        )

    # Create the subtask
    subtask = Subtask(
        task_id=subtask_data.task_id,
        title=subtask_data.title,
        description=subtask_data.description,
        description_html=subtask_data.description_html,
        deliverables=[d.model_dump() for d in subtask_data.deliverables] if subtask_data.deliverables else None,
        acceptance_criteria=subtask_data.acceptance_criteria,
        references=[r.model_dump() for r in subtask_data.references] if subtask_data.references else None,
        attachments=[a.model_dump() for a in subtask_data.attachments] if subtask_data.attachments else None,
        example_output=subtask_data.example_output,
        tools_required=subtask_data.tools_required,
        estimated_hours=subtask_data.estimated_hours,
        subtask_type=subtask_data.subtask_type,
        sequence_order=subtask_data.sequence_order,
        budget_allocation_percent=subtask_data.budget_allocation_percent,
        budget_cngn=subtask_data.budget_cngn,
        deadline=subtask_data.deadline,
        status="open",
    )
    db.add(subtask)

    # Update task status to decomposed if it was just funded
    if task.status == "funded":
        task.status = "decomposed"

    await db.flush()
    await db.refresh(subtask)

    return SubtaskResponse.model_validate(subtask)


@router.patch("/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    subtask_id: UUID,
    subtask_data: SubtaskUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> SubtaskResponse:
    """
    Update a subtask.
    Only the task owner or admin can update subtasks.
    Can only update subtasks that are not yet claimed.

    Args:
        subtask_id: The subtask ID
        subtask_data: The update data
        db: Database session
        current_user: The authenticated user

    Returns:
        The updated subtask
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()

    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )

    # Get parent task for authorization
    task_result = await db.execute(select(Task).where(Task.id == subtask.task_id))
    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check authorization
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this subtask",
        )

    # Check subtask status - can only update open subtasks (unless admin)
    if subtask.status != "open" and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update subtask that has been claimed or completed",
        )

    # Apply updates
    update_data = subtask_data.model_dump(exclude_unset=True)

    # Handle nested objects specially
    if "deliverables" in update_data and update_data["deliverables"] is not None:
        update_data["deliverables"] = [d.model_dump() if hasattr(d, 'model_dump') else d for d in update_data["deliverables"]]
    if "references" in update_data and update_data["references"] is not None:
        update_data["references"] = [r.model_dump() if hasattr(r, 'model_dump') else r for r in update_data["references"]]
    if "attachments" in update_data and update_data["attachments"] is not None:
        update_data["attachments"] = [a.model_dump() if hasattr(a, 'model_dump') else a for a in update_data["attachments"]]

    for key, value in update_data.items():
        setattr(subtask, key, value)

    await db.flush()
    await db.refresh(subtask)

    return SubtaskResponse.model_validate(subtask)


@router.delete("/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete a subtask.
    Only the task owner or admin can delete subtasks.
    Can only delete subtasks that are not yet claimed.

    Args:
        subtask_id: The subtask ID
        db: Database session
        current_user: The authenticated user
    """
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()

    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )

    # Get parent task for authorization
    task_result = await db.execute(select(Task).where(Task.id == subtask.task_id))
    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check authorization
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this subtask",
        )

    # Check subtask status - can only delete open subtasks (unless admin)
    if subtask.status != "open" and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete subtask that has been claimed or completed",
        )

    await db.delete(subtask)
    await db.flush()


class ReorderRequest(BaseModel):
    """Request schema for reordering subtasks."""
    subtask_ids: list[UUID] = Field(..., description="Ordered list of subtask IDs")


@router.post("/reorder/{task_id}", response_model=list[SubtaskResponse])
async def reorder_subtasks(
    task_id: UUID,
    reorder_data: ReorderRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> list[SubtaskResponse]:
    """
    Reorder subtasks within a task.
    Only the task owner or admin can reorder subtasks.

    Args:
        task_id: The parent task ID
        reorder_data: The new ordering of subtask IDs
        db: Database session
        current_user: The authenticated user

    Returns:
        The reordered subtasks
    """
    # Get the task
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check authorization
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reorder subtasks for this task",
        )

    # Get all subtasks for this task
    subtasks_result = await db.execute(
        select(Subtask).where(Subtask.task_id == task_id)
    )
    subtasks = {st.id: st for st in subtasks_result.scalars().all()}

    # Validate that all provided IDs belong to this task
    if set(reorder_data.subtask_ids) != set(subtasks.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subtask IDs must match exactly the subtasks belonging to this task",
        )

    # Update sequence_order for each subtask
    for idx, subtask_id in enumerate(reorder_data.subtask_ids, start=1):
        subtasks[subtask_id].sequence_order = idx

    await db.flush()

    # Return subtasks in new order
    ordered_subtasks = [subtasks[sid] for sid in reorder_data.subtask_ids]
    return [SubtaskResponse.model_validate(st) for st in ordered_subtasks]
