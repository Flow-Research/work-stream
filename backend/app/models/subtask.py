"""Subtask database model."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User
    from app.models.submission import Submission


class Subtask(Base):
    """Subtask model representing decomposed task units."""
    
    __tablename__ = "subtasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        nullable=False,
        index=True,
    )
    
    # Details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deliverables: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    acceptance_criteria: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    references: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    attachments: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    example_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tools_required: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Type: discovery, extraction, mapping, assembly, narrative
    subtask_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Budget
    budget_allocation_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    budget_cngn: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    
    # Status: open, claimed, in_progress, submitted, approved, rejected, disputed
    status: Mapped[str] = mapped_column(
        String(20),
        default="open",
        index=True,
    )
    
    # Assignment
    claimed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Collaborators
    collaborators: Mapped[Optional[list[uuid.UUID]]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
    )
    collaborator_splits: Mapped[Optional[list[Decimal]]] = mapped_column(
        ARRAY(Numeric(5, 2)),
        nullable=True,
    )
    
    # Review
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    auto_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Deadline
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")
    worker: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[claimed_by],
    )
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="subtask",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Subtask {self.title[:50]}>"
