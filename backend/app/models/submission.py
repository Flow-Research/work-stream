"""Submission database model."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.subtask import Subtask
    from app.models.user import User


class Submission(Base):
    """Submission model representing work submitted for subtasks."""
    
    __tablename__ = "submissions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    subtask_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subtasks.id"),
        nullable=False,
        index=True,
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    
    # Content
    content_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Artifact
    artifact_ipfs_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    artifact_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # json, csv, md
    artifact_on_chain_hash: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    artifact_on_chain_tx: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    
    # Status: pending, approved, rejected
    status: Mapped[str] = mapped_column(String(20), default="pending")
    
    # Review
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Payment
    payment_tx_hash: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    payment_amount_cngn: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    
    # Relationships
    subtask: Mapped["Subtask"] = relationship("Subtask", back_populates="submissions")
    submitter: Mapped["User"] = relationship("User", foreign_keys=[submitted_by])
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self) -> str:
        return f"<Submission {self.id}>"
