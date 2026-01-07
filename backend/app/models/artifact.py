"""Artifact database models."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Artifact(Base):
    """Artifact model representing reusable outputs for licensing."""
    
    __tablename__ = "artifacts"
    
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
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # dataset, knowledge_graph
    
    # Storage
    ipfs_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    on_chain_hash: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    on_chain_tx: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    schema_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Contributors
    contributors: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
    )
    contributor_shares: Mapped[list[Decimal]] = mapped_column(
        ARRAY(Numeric(5, 2)),
        nullable=False,
    )
    
    # Earnings
    total_earnings_cngn: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=0,
    )
    
    # Listing
    is_listed: Mapped[bool] = mapped_column(Boolean, default=False)
    listed_price_cngn: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )
    
    # Royalty terms
    royalty_cap_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(3, 1),
        default=Decimal("5.0"),
    )
    royalty_expiry_years: Mapped[int] = mapped_column(Integer, default=3)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<Artifact {self.title[:50]}>"


class ArtifactPurchase(Base):
    """ArtifactPurchase model for royalty tracking."""
    
    __tablename__ = "artifact_purchases"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    artifact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artifacts.id"),
        nullable=False,
    )
    
    # Buyer
    buyer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    buyer_wallet: Mapped[Optional[str]] = mapped_column(String(42), nullable=True)
    
    # Payment
    amount_cngn: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    platform_fee_cngn: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    payment_tx_hash: Mapped[Optional[str]] = mapped_column(String(66), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    
    def __repr__(self) -> str:
        return f"<ArtifactPurchase {self.id}>"
