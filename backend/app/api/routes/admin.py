"""Admin endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.api.deps import AdminUser, DbSession
from app.models.user import User
from app.models.dispute import Dispute
from app.models.subtask import Subtask
from app.models.task import Task
from pydantic import BaseModel

from app.schemas.user import UserResponse
from app.schemas.dispute import DisputeListResponse, DisputeResolveRequest, DisputeResponse

router = APIRouter()


class UserListResponse(BaseModel):
    """Response schema for user list."""
    
    users: list[UserResponse]
    total: int
    page: int
    limit: int


class BanUserRequest(BaseModel):
    """Request schema for banning a user."""
    
    reason: str


@router.get("/users", response_model=UserListResponse)
async def list_users(
    db: DbSession,
    admin: AdminUser,
    verified: Optional[bool] = Query(None),
    banned: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    """
    List all users (admin only).
    
    Args:
        db: Database session
        admin: The admin user
        verified: Filter by verification status
        banned: Filter by ban status
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated list of users
    """
    query = select(User)
    count_query = select(func.count(User.id))
    
    if verified is not None:
        query = query.where(User.id_verified == verified)
        count_query = count_query.where(User.id_verified == verified)
    
    if banned is not None:
        query = query.where(User.is_banned == banned)
        count_query = count_query.where(User.is_banned == banned)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/users/{user_id}/verify", response_model=UserResponse)
async def verify_user(
    user_id: UUID,
    db: DbSession,
    admin: AdminUser,
) -> UserResponse:
    """
    Verify a user's ID (admin only).
    
    Args:
        user_id: The user ID
        db: Database session
        admin: The admin user
        
    Returns:
        The verified user
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.id_verified = True
    user.id_verified_at = datetime.utcnow()
    user.id_verified_by = admin.id
    
    await db.flush()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/ban", response_model=UserResponse)
async def ban_user(
    user_id: UUID,
    ban_request: BanUserRequest,
    db: DbSession,
    admin: AdminUser,
) -> UserResponse:
    """
    Ban a user (admin only).
    
    Args:
        user_id: The user ID
        ban_request: The ban reason
        db: Database session
        admin: The admin user
        
    Returns:
        The banned user
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban an admin user",
        )
    
    user.is_banned = True
    user.banned_reason = ban_request.reason
    
    await db.flush()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/unban", response_model=UserResponse)
async def unban_user(
    user_id: UUID,
    db: DbSession,
    admin: AdminUser,
) -> UserResponse:
    """
    Unban a user (admin only).
    
    Args:
        user_id: The user ID
        db: Database session
        admin: The admin user
        
    Returns:
        The unbanned user
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_banned = False
    user.banned_reason = None
    
    await db.flush()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get("/disputes", response_model=DisputeListResponse)
async def list_disputes(
    db: DbSession,
    admin: AdminUser,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> DisputeListResponse:
    """
    List all disputes (admin only).
    
    Args:
        db: Database session
        admin: The admin user
        status_filter: Filter by dispute status
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated list of disputes
    """
    query = select(Dispute)
    count_query = select(func.count(Dispute.id))
    
    if status_filter:
        query = query.where(Dispute.status == status_filter)
        count_query = count_query.where(Dispute.status == status_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Dispute.created_at.desc())
    
    result = await db.execute(query)
    disputes = result.scalars().all()
    
    return DisputeListResponse(
        disputes=[DisputeResponse.model_validate(d) for d in disputes],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/disputes/{dispute_id}/resolve", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: UUID,
    resolve_request: DisputeResolveRequest,
    db: DbSession,
    admin: AdminUser,
) -> DisputeResponse:
    """
    Resolve a dispute (admin only).
    
    Args:
        dispute_id: The dispute ID
        resolve_request: The resolution details
        db: Database session
        admin: The admin user
        
    Returns:
        The resolved dispute
    """
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found",
        )
    
    if dispute.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute is not open",
        )
    
    dispute.status = "resolved"
    dispute.resolution = resolve_request.resolution
    dispute.resolved_by = admin.id
    dispute.resolved_at = datetime.utcnow()
    dispute.winner_id = resolve_request.winner_id
    
    # Update subtask status
    subtask_result = await db.execute(
        select(Subtask).where(Subtask.id == dispute.subtask_id)
    )
    subtask = subtask_result.scalar_one_or_none()
    
    if subtask:
        # If worker won, mark as approved
        if subtask.claimed_by == resolve_request.winner_id:
            subtask.status = "approved"
            subtask.approved_at = datetime.utcnow()
            subtask.approved_by = admin.id
        else:
            # Client won, mark as rejected
            subtask.status = "rejected"
        
        # Update task status
        task_result = await db.execute(
            select(Task).where(Task.id == subtask.task_id)
        )
        task = task_result.scalar_one_or_none()
        if task:
            task.status = "in_progress"
    
    # Update reputation
    winner_result = await db.execute(
        select(User).where(User.id == resolve_request.winner_id)
    )
    winner = winner_result.scalar_one_or_none()
    if winner:
        winner.disputes_won += 1
    
    # Find loser
    if dispute.raised_by == resolve_request.winner_id:
        # Winner raised the dispute, loser is the other party
        if subtask and subtask.claimed_by != resolve_request.winner_id:
            loser_result = await db.execute(
                select(User).where(User.id == subtask.claimed_by)
            )
        else:
            # Look up task client
            if task:
                loser_result = await db.execute(
                    select(User).where(User.id == task.client_id)
                )
            else:
                loser_result = None
    else:
        loser_result = await db.execute(
            select(User).where(User.id == dispute.raised_by)
        )
    
    if loser_result:
        loser = loser_result.scalar_one_or_none()
        if loser:
            loser.disputes_lost += 1
    
    await db.flush()
    await db.refresh(dispute)
    
    return DisputeResponse.model_validate(dispute)
