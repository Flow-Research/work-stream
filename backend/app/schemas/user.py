"""User schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., min_length=2, max_length=2)
    bio: Optional[str] = None
    skills: Optional[list[str]] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    wallet_address: str = Field(
        ...,
        min_length=42,
        max_length=42,
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    bio: Optional[str] = None
    skills: Optional[list[str]] = None


class UserResponse(BaseModel):
    """Response schema for user data."""
    
    id: UUID
    wallet_address: str
    name: str
    country: str
    bio: Optional[str]
    skills: Optional[list[str]]
    
    id_verified: bool
    id_verified_at: Optional[datetime]
    
    reputation_score: int
    reputation_tier: str
    tasks_completed: int
    tasks_approved: int
    
    is_admin: bool
    is_banned: bool
    
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    """Public response schema for user data (limited info)."""
    
    id: UUID
    name: str
    country: str
    bio: Optional[str]
    skills: Optional[list[str]]
    
    reputation_tier: str
    tasks_completed: int
    
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UserVerifyIdRequest(BaseModel):
    """Request schema for ID verification."""
    
    national_id: str = Field(..., min_length=5, max_length=50)
    # Document will be uploaded as file
