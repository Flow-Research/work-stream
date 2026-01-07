"""Task database model."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.subtask import Subtask
    from app.models.user import User


class Task(Base):
    """Task model representing research projects."""
    
    __tablename__ = "tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    research_question: Mapped[str] = mapped_column(Text, nullable=False)
    background_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    methodology_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_outcomes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    references: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    attachments: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    
    # Status: draft, funded, decomposed, in_progress, in_review, completed, cancelled, disputed
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        index=True,
    )
    
    # Budget
    total_budget_cngn: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    
    # Escrow
    escrow_tx_hash: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    escrow_contract_task_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Requirements
    skills_required: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
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
    funded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])
    subtasks: Mapped[list["Subtask"]] = relationship(
        "Subtask",
        back_populates="task",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Task {self.title[:50]}>"
