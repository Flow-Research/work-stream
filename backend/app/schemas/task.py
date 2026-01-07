"""Task schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReferenceItem(BaseModel):
    id: str
    type: str
    title: str
    url: str
    description: Optional[str] = None
    required: bool = False


class AttachmentItem(BaseModel):
    id: str
    filename: str
    mime_type: str
    size_bytes: int
    ipfs_hash: str
    description: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    uploaded_by: Optional[UUID] = None


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    description_html: Optional[str] = None
    research_question: str = Field(..., min_length=1)
    background_context: Optional[str] = None
    methodology_notes: Optional[str] = None
    expected_outcomes: Optional[list[str]] = None
    references: Optional[list[ReferenceItem]] = None
    attachments: Optional[list[AttachmentItem]] = None
    skills_required: Optional[list[str]] = None
    deadline: Optional[datetime] = None


class TaskCreate(TaskBase):
    total_budget_cngn: Decimal = Field(..., gt=0, decimal_places=2)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    description_html: Optional[str] = None
    research_question: Optional[str] = None
    background_context: Optional[str] = None
    methodology_notes: Optional[str] = None
    expected_outcomes: Optional[list[str]] = None
    references: Optional[list[ReferenceItem]] = None
    attachments: Optional[list[AttachmentItem]] = None
    skills_required: Optional[list[str]] = None
    deadline: Optional[datetime] = None


class TaskFundRequest(BaseModel):
    """Request schema for funding a task."""
    
    escrow_tx_hash: str = Field(
        ...,
        min_length=66,
        max_length=66,
        pattern=r"^0x[a-fA-F0-9]{64}$",
    )


class SubtaskBrief(BaseModel):
    """Brief subtask info for task response."""
    
    id: UUID
    title: str
    subtask_type: str
    status: str
    budget_cngn: Decimal
    claimed_by: Optional[UUID]
    
    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    """Response schema for task data."""
    
    id: UUID
    title: str
    description: str
    description_html: Optional[str] = None
    research_question: str
    background_context: Optional[str] = None
    methodology_notes: Optional[str] = None
    expected_outcomes: Optional[list[str]] = None
    references: Optional[list[ReferenceItem]] = None
    attachments: Optional[list[AttachmentItem]] = None
    
    client_id: UUID
    status: str
    
    total_budget_cngn: Decimal
    escrow_tx_hash: Optional[str] = None
    escrow_contract_task_id: Optional[int] = None
    
    skills_required: Optional[list[str]] = None
    deadline: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    funded_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    subtasks: Optional[list[SubtaskBrief]] = None
    
    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Response schema for task list."""
    
    tasks: list[TaskResponse]
    total: int
    page: int
    limit: int
