"""Subtask schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.task import ReferenceItem, AttachmentItem


class DeliverableItem(BaseModel):
    """Schema for a deliverable item."""
    id: str
    title: str
    description: str
    type: str  # file, text, dataset, code, analysis
    required: bool = True
    format_hint: Optional[str] = None  # e.g., "CSV", "JSON", "Markdown"


class SubtaskBase(BaseModel):
    """Base subtask schema."""
    
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    description_html: Optional[str] = None
    deliverables: Optional[list[DeliverableItem]] = None
    acceptance_criteria: Optional[list[str]] = None
    references: Optional[list[ReferenceItem]] = None
    attachments: Optional[list[AttachmentItem]] = None
    example_output: Optional[str] = None
    tools_required: Optional[list[str]] = None
    estimated_hours: Optional[Decimal] = Field(None, ge=0, le=999)
    subtask_type: str = Field(
        ...,
        pattern=r"^(discovery|extraction|mapping|assembly|narrative)$",
    )
    sequence_order: int = Field(..., ge=1)
    budget_allocation_percent: Decimal = Field(..., gt=0, le=100)


class SubtaskCreate(SubtaskBase):
    """Schema for creating a subtask."""
    
    task_id: UUID
    budget_cngn: Decimal = Field(..., gt=0)
    deadline: Optional[datetime] = None


class SubtaskUpdate(BaseModel):
    """Schema for updating a subtask."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    description_html: Optional[str] = None
    deliverables: Optional[list[DeliverableItem]] = None
    acceptance_criteria: Optional[list[str]] = None
    references: Optional[list[ReferenceItem]] = None
    attachments: Optional[list[AttachmentItem]] = None
    example_output: Optional[str] = None
    tools_required: Optional[list[str]] = None
    estimated_hours: Optional[Decimal] = Field(None, ge=0, le=999)
    deadline: Optional[datetime] = None


class SubtaskClaimRequest(BaseModel):
    """Request schema for claiming a subtask."""
    
    collaborators: Optional[list[str]] = Field(
        None,
        description="List of collaborator wallet addresses",
    )
    splits: Optional[list[Decimal]] = Field(
        None,
        description="Payment splits for collaborators (must sum to 100)",
    )


class SubtaskReviewRequest(BaseModel):
    """Request schema for approving or rejecting a subtask."""
    
    review_notes: Optional[str] = Field(
        None,
        description="Notes explaining the review decision",
    )


class SubtaskRejectRequest(BaseModel):
    """Request schema for rejecting a subtask (review_notes required)."""
    
    review_notes: str = Field(
        ...,
        min_length=1,
        description="Notes explaining why the submission was rejected",
    )


class SubtaskResponse(BaseModel):
    """Response schema for subtask data."""
    
    id: UUID
    task_id: UUID
    
    title: str
    description: str
    description_html: Optional[str] = None
    deliverables: Optional[list[DeliverableItem]] = None
    acceptance_criteria: Optional[list[str]] = None
    references: Optional[list[ReferenceItem]] = None
    attachments: Optional[list[AttachmentItem]] = None
    example_output: Optional[str] = None
    tools_required: Optional[list[str]] = None
    estimated_hours: Optional[Decimal] = None
    
    subtask_type: str
    sequence_order: int
    
    budget_allocation_percent: Decimal
    budget_cngn: Decimal
    
    status: str
    
    claimed_by: Optional[UUID] = None
    claimed_at: Optional[datetime] = None
    collaborators: Optional[list[UUID]] = None
    collaborator_splits: Optional[list[Decimal]] = None
    
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    auto_approved: bool = False
    
    deadline: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SubtaskListResponse(BaseModel):
    """Response schema for subtask list."""
    
    subtasks: list[SubtaskResponse]
    total: int
    page: int
    limit: int
