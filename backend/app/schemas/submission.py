"""Submission schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    """Schema for creating a submission."""
    
    content_summary: str = Field(..., min_length=1)
    # Artifact file will be uploaded separately


class SubmissionResponse(BaseModel):
    """Response schema for submission data."""
    
    id: UUID
    subtask_id: UUID
    submitted_by: UUID
    
    content_summary: Optional[str]
    
    artifact_ipfs_hash: Optional[str]
    artifact_type: Optional[str]
    artifact_on_chain_hash: Optional[str]
    artifact_on_chain_tx: Optional[str]
    
    status: str
    
    review_notes: Optional[str]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    
    payment_tx_hash: Optional[str]
    payment_amount_cngn: Optional[Decimal]
    
    created_at: datetime
    
    model_config = {"from_attributes": True}


class SubmissionReviewRequest(BaseModel):
    """Request schema for reviewing a submission."""
    
    approved: bool
    review_notes: Optional[str] = None


class SubmissionListResponse(BaseModel):
    """Response schema for submission list."""
    
    submissions: list[SubmissionResponse]
    total: int
