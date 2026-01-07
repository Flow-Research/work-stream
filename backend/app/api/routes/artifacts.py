"""Artifact endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DbSession
from app.models.artifact import Artifact, ArtifactPurchase
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactListRequest,
    ArtifactListResponse,
    ArtifactPurchaseRequest,
    ArtifactResponse,
)

router = APIRouter()


@router.get("", response_model=ArtifactListResponse)
async def list_artifacts(
    db: DbSession,
    task_id: Optional[UUID] = Query(None),
    is_listed: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ArtifactListResponse:
    """
    List artifacts with optional filtering.
    
    Args:
        db: Database session
        task_id: Filter by task ID
        is_listed: Filter by listing status
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated list of artifacts
    """
    query = select(Artifact)
    count_query = select(func.count(Artifact.id))
    
    if task_id:
        query = query.where(Artifact.task_id == task_id)
        count_query = count_query.where(Artifact.task_id == task_id)
    
    if is_listed is not None:
        query = query.where(Artifact.is_listed == is_listed)
        count_query = count_query.where(Artifact.is_listed == is_listed)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Artifact.created_at.desc())
    
    result = await db.execute(query)
    artifacts = result.scalars().all()
    
    return ArtifactListResponse(
        artifacts=[ArtifactResponse.model_validate(a) for a in artifacts],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: UUID,
    db: DbSession,
) -> ArtifactResponse:
    """
    Get a specific artifact.
    
    Args:
        artifact_id: The artifact ID
        db: Database session
        
    Returns:
        The artifact data
    """
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )
    
    return ArtifactResponse.model_validate(artifact)


@router.post("/{artifact_id}/list", response_model=ArtifactResponse)
async def list_artifact(
    artifact_id: UUID,
    list_request: ArtifactListRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> ArtifactResponse:
    """
    List an artifact for sale.
    
    Args:
        artifact_id: The artifact ID
        list_request: The listing request
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The listed artifact
    """
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )
    
    # Check if user is a contributor
    if current_user.id not in artifact.contributors and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list this artifact",
        )
    
    artifact.is_listed = True
    artifact.listed_price_cngn = list_request.price_cngn
    
    await db.flush()
    await db.refresh(artifact)
    
    return ArtifactResponse.model_validate(artifact)


@router.post("/{artifact_id}/purchase", response_model=ArtifactResponse)
async def purchase_artifact(
    artifact_id: UUID,
    purchase_request: ArtifactPurchaseRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> ArtifactResponse:
    """
    Purchase an artifact.
    
    Args:
        artifact_id: The artifact ID
        purchase_request: The purchase request
        current_user: The authenticated user
        db: Database session
        
    Returns:
        The artifact with download info
    """
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )
    
    if not artifact.is_listed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artifact is not listed for sale",
        )
    
    # Calculate platform fee (10%)
    from decimal import Decimal
    platform_fee = artifact.listed_price_cngn * Decimal("0.10")
    
    # Record purchase
    purchase = ArtifactPurchase(
        artifact_id=artifact_id,
        buyer_id=current_user.id,
        amount_cngn=artifact.listed_price_cngn,
        platform_fee_cngn=platform_fee,
        payment_tx_hash=purchase_request.payment_tx_hash,
    )
    db.add(purchase)
    
    # Update total earnings
    artifact.total_earnings_cngn += artifact.listed_price_cngn
    
    await db.flush()
    await db.refresh(artifact)
    
    return ArtifactResponse.model_validate(artifact)
