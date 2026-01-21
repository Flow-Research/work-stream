"""Skill and SkillCategory schemas for API validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
import re


def to_slug(name: str) -> str:
    """Convert a name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug


# ============ Skill Category Schemas ============

class SkillCategoryBase(BaseModel):
    """Base schema for skill category."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # hex color
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class SkillCategoryCreate(SkillCategoryBase):
    """Schema for creating a skill category."""
    pass


class SkillCategoryUpdate(BaseModel):
    """Schema for updating a skill category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SkillCategoryResponse(SkillCategoryBase):
    """Schema for skill category response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillCategoryWithSkillsResponse(SkillCategoryResponse):
    """Schema for skill category response including skills."""
    skills: list["SkillResponse"] = []


# ============ Skill Schemas ============

class SkillBase(BaseModel):
    """Base schema for skill."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class SkillCreate(SkillBase):
    """Schema for creating a skill."""
    slug: Optional[str] = Field(None, max_length=100)

    def model_post_init(self, __context) -> None:
        """Generate slug from name if not provided."""
        if not self.slug:
            object.__setattr__(self, 'slug', to_slug(self.name))


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SkillResponse(BaseModel):
    """Schema for skill response."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    category_id: Optional[UUID]
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillWithCategoryResponse(SkillResponse):
    """Schema for skill response including category details."""
    category: Optional[SkillCategoryResponse] = None


class SkillListResponse(BaseModel):
    """Schema for paginated skill list response."""
    skills: list[SkillResponse]
    total: int


class SkillCategoryListResponse(BaseModel):
    """Schema for skill categories list with nested skills."""
    categories: list[SkillCategoryWithSkillsResponse]
    uncategorized: list[SkillResponse]


# Update forward references
SkillCategoryWithSkillsResponse.model_rebuild()
