"""Artifact schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ArtifactCreate(BaseModel):
    """Schema for creating an artifact."""
    
    task_id: UUID
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    artifact_type: str = Field(
        ...,
        pattern=r"^(dataset|knowledge_graph)$",
    )
    ipfs_hash: str = Field(..., min_length=46, max_length=64)
    contributors: list[UUID]
    contributor_shares: list[Decimal]


class ArtifactResponse(BaseModel):
    """Response schema for artifact data."""
    
    id: UUID
    task_id: UUID
    
    title: str
    description: Optional[str]
    artifact_type: str
    
    ipfs_hash: str
    on_chain_hash: Optional[str]
    on_chain_tx: Optional[str]
    schema_version: Optional[str]
    
    contributors: list[UUID]
    contributor_shares: list[Decimal]
    
    total_earnings_cngn: Decimal
    
    is_listed: bool
    listed_price_cngn: Optional[Decimal]
    
    royalty_cap_multiplier: Decimal
    royalty_expiry_years: int
    
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ArtifactListRequest(BaseModel):
    """Request schema for listing an artifact."""
    
    price_cngn: Decimal = Field(..., gt=0)


class ArtifactPurchaseRequest(BaseModel):
    """Request schema for purchasing an artifact."""
    
    payment_tx_hash: str = Field(
        ...,
        min_length=66,
        max_length=66,
        pattern=r"^0x[a-fA-F0-9]{64}$",
    )


class ArtifactListResponse(BaseModel):
    """Response schema for artifact list."""
    
    artifacts: list[ArtifactResponse]
    total: int
    page: int
    limit: int
