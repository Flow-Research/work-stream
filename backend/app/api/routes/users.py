"""User endpoints."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.models.user import User
from app.schemas.user import UserPublicResponse, UserResponse, UserUpdate
from sqlalchemy import select

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get the current user's profile.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        The user's profile data
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> UserResponse:
    """
    Update the current user's profile.
    
    Args:
        update_data: The fields to update
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The updated user profile
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(current_user, field, value)
    
    await db.flush()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_public_profile(
    user_id: UUID,
    db: DbSession,
) -> UserPublicResponse:
    """
    Get a user's public profile.
    
    Args:
        user_id: The user's ID
        db: Database session
        
    Returns:
        The user's public profile data
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserPublicResponse.model_validate(user)


def calculate_reputation_score(user: User) -> int:
    """
    Calculate a user's reputation score.
    
    Args:
        user: The user to calculate score for
        
    Returns:
        The calculated reputation score
    """
    base_score = 0
    
    # Tasks completed (+10 each, max 500)
    base_score += min(user.tasks_completed * 10, 500)
    
    # Approval rate bonus
    if user.tasks_completed > 0:
        approval_rate = user.tasks_approved / user.tasks_completed
        base_score += int(approval_rate * 200)  # Max 200
    
    # Dispute record
    base_score += user.disputes_won * 20
    base_score -= user.disputes_lost * 50
    
    # Floor at 0
    return max(base_score, 0)


def calculate_tier(score: int, tasks_completed: int, tasks_approved: int) -> str:
    """
    Calculate a user's reputation tier.
    
    Args:
        score: The user's reputation score
        tasks_completed: Number of tasks completed
        tasks_approved: Number of tasks approved
        
    Returns:
        The reputation tier
    """
    if tasks_completed == 0:
        return "new"
    
    approval_rate = tasks_approved / tasks_completed
    
    if tasks_completed >= 50 and approval_rate >= 0.9 and score >= 600:
        return "expert"
    elif tasks_completed >= 20 and approval_rate >= 0.8 and score >= 300:
        return "established"
    elif tasks_completed >= 5 and score >= 50:
        return "active"
    else:
        return "new"
