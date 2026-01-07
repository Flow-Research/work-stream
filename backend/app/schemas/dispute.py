"""Dispute schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DisputeCreate(BaseModel):
    """Schema for creating a dispute."""
    
    reason: str = Field(..., min_length=10)


class DisputeResolveRequest(BaseModel):
    """Request schema for resolving a dispute."""
    
    winner_id: UUID
    resolution: str = Field(..., min_length=10)


class DisputeResponse(BaseModel):
    """Response schema for dispute data."""
    
    id: UUID
    subtask_id: UUID
    raised_by: UUID
    
    reason: str
    status: str
    
    resolution: Optional[str]
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
    winner_id: Optional[UUID]
    
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DisputeListResponse(BaseModel):
    """Response schema for dispute list."""
    
    disputes: list[DisputeResponse]
    total: int
    page: int
    limit: int
