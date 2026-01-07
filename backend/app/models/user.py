"""User database model."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """User model representing platform participants."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    wallet_address: Mapped[str] = mapped_column(
        String(42),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)  # ISO code
    
    # ID verification
    national_id_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    id_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    id_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    id_verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    
    # Profile
    skills: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Reputation
    reputation_score: Mapped[int] = mapped_column(Integer, default=0)
    reputation_tier: Mapped[str] = mapped_column(
        String(20),
        default="new",
    )  # new, active, established, expert
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_approved: Mapped[int] = mapped_column(Integer, default=0)
    disputes_won: Mapped[int] = mapped_column(Integer, default=0)
    disputes_lost: Mapped[int] = mapped_column(Integer, default=0)
    
    # Admin
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    banned_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
    
    def __repr__(self) -> str:
        return f"<User {self.wallet_address}>"
