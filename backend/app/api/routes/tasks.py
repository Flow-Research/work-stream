"""Task endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models.task import Task
from app.models.subtask import Subtask
from app.schemas.task import (
    TaskCreate,
    TaskFundRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.blockchain import BlockchainService

router = APIRouter()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: DbSession,
    status_filter: Optional[str] = Query(None, alias="status"),
    skills: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    include_drafts: bool = Query(False, description="Include draft tasks (admin/creator only)"),
    current_user_id: Optional[str] = Query(None, alias="user_id", description="Current user ID for filtering own drafts"),
) -> TaskListResponse:
    """
    List all tasks with optional filtering.

    Draft tasks are hidden by default and only visible to their creator or admin.
    Search supports both fuzzy matching (partial) and exact matching.

    Args:
        db: Database session
        status_filter: Filter by task status
        skills: Filter by required skills (comma-separated)
        search: Search query for title and description
        page: Page number
        limit: Items per page
        include_drafts: Whether to include draft tasks
        current_user_id: Current user ID (for draft filtering)

    Returns:
        Paginated list of tasks
    """
    from sqlalchemy import or_

    query = select(Task)
    count_query = select(func.count(Task.id))

    # Filter out draft tasks from public list (unless specific status filter is applied)
    if not status_filter or status_filter != "draft":
        if not include_drafts:
            query = query.where(Task.status != "draft")
            count_query = count_query.where(Task.status != "draft")

    # Apply status filter
    if status_filter:
        query = query.where(Task.status == status_filter)
        count_query = count_query.where(Task.status == status_filter)

    # Apply search filter (fuzzy matching using ILIKE)
    if search:
        search_pattern = f"%{search}%"
        search_filter = or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern),
            Task.research_question.ilike(search_pattern),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if skills:
        skill_list = [s.strip() for s in skills.split(",")]
        query = query.where(Task.skills_required.overlap(skill_list))
        count_query = count_query.where(Task.skills_required.overlap(skill_list))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Task.created_at.desc())

    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: DbSession,
) -> TaskResponse:
    """
    Get a specific task by ID.
    
    Args:
        task_id: The task ID
        db: Database session
        
    Returns:
        The task data with subtasks
        
    Raises:
        HTTPException: If task not found
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    return TaskResponse.model_validate(task)


@router.post("", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: AdminUser,  # Admin only for MVP
    db: DbSession,
) -> TaskResponse:
    """
    Create a new task (admin only for MVP).
    
    Args:
        task_data: The task data
        current_user: The admin user
        db: Database session
        
    Returns:
        The created task
    """
    task = Task(
        **task_data.model_dump(),
        client_id=current_user.id,
        status="draft",
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/fund", response_model=TaskResponse)
async def fund_task(
    task_id: UUID,
    fund_request: TaskFundRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> TaskResponse:
    """
    Record funding of a task after escrow deposit.
    
    Args:
        task_id: The task ID
        fund_request: The funding info (escrow tx hash)
        current_user: The authenticated user (must be client)
        db: Database session
        
    Returns:
        The updated task
        
    Raises:
        HTTPException: If task not found or not authorized
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to fund this task",
        )
    
    if task.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not in draft status",
        )
    
    blockchain = BlockchainService()
    if blockchain.is_configured():
        tx_info = blockchain.verify_transaction(fund_request.escrow_tx_hash)
        if not tx_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not verify transaction on blockchain",
            )
        if tx_info.get("status") != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction failed on blockchain",
            )
        task.escrow_contract_task_id = blockchain.get_task_counter()
    
    task.escrow_tx_hash = fund_request.escrow_tx_hash
    task.status = "funded"
    task.funded_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    update_data: TaskUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> TaskResponse:
    """
    Update a task.
    
    Args:
        task_id: The task ID
        update_data: The fields to update
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The updated task
        
    Raises:
        HTTPException: If task not found or not authorized
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )
    
    if task.status not in ("draft", "funded"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update task in current status",
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(task, field, value)
    
    await db.flush()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> TaskResponse:
    """
    Cancel a task (before work starts).
    
    Args:
        task_id: The task ID
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The cancelled task
        
    Raises:
        HTTPException: If task not found or cannot be cancelled
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this task",
        )
    
    if task.status not in ("draft", "funded", "decomposed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel task in current status",
        )
    
    # Check if any subtasks are in progress
    subtask_result = await db.execute(
        select(Subtask).where(
            Subtask.task_id == task_id,
            Subtask.status.in_(["claimed", "in_progress", "submitted"])
        )
    )
    active_subtasks = subtask_result.scalars().all()
    
    if active_subtasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel task with active subtasks",
        )
    
    task.status = "cancelled"
    await db.flush()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> TaskResponse:
    """
    Mark a task as complete (all subtasks approved).
    
    Args:
        task_id: The task ID
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The completed task
        
    Raises:
        HTTPException: If task not found or cannot be completed
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    if task.client_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this task",
        )
    
    # Check all subtasks are approved
    subtask_result = await db.execute(
        select(Subtask).where(Subtask.task_id == task_id)
    )
    subtasks = subtask_result.scalars().all()
    
    if not subtasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task has no subtasks",
        )
    
    all_approved = all(st.status == "approved" for st in subtasks)
    if not all_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not all subtasks are approved",
        )
    
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(task)
    
    return TaskResponse.model_validate(task)
