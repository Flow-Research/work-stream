"""API routes for skills and skill categories management."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.skill import Skill, SkillCategory
from app.schemas.skill import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
    SkillWithCategoryResponse,
    SkillListResponse,
    SkillCategoryCreate,
    SkillCategoryUpdate,
    SkillCategoryResponse,
    SkillCategoryWithSkillsResponse,
    SkillCategoryListResponse,
    to_slug,
)
from app.api.deps import get_current_user_optional, get_admin_user
from app.models.user import User

router = APIRouter()


# ============ Public Endpoints ============

@router.get("", response_model=SkillListResponse)
async def list_skills(
    db: AsyncSession = Depends(get_db),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search skills by name"),
    include_inactive: bool = Query(False, description="Include inactive skills (admin only)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> SkillListResponse:
    """
    List all skills, optionally filtered by category.
    Public endpoint - returns only active skills unless admin requests inactive.
    """
    query = select(Skill).order_by(Skill.display_order, Skill.name)

    # Only admins can see inactive skills
    if not include_inactive or not current_user or not current_user.is_admin:
        query = query.where(Skill.is_active == True)

    if category_id:
        query = query.where(Skill.category_id == category_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(Skill.name.ilike(search_pattern))

    # Count query
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Execute main query
    result = await db.execute(query)
    skills = result.scalars().all()

    return SkillListResponse(
        skills=[SkillResponse.model_validate(s) for s in skills],
        total=total,
    )


@router.get("/grouped", response_model=SkillCategoryListResponse)
async def list_skills_grouped(
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False, description="Include inactive skills/categories"),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> SkillCategoryListResponse:
    """
    List all skills grouped by category.
    Returns categories with their skills, plus uncategorized skills.
    """
    only_active = not include_inactive or not current_user or not current_user.is_admin

    # Get categories with skills
    cat_query = (
        select(SkillCategory)
        .options(selectinload(SkillCategory.skills))
        .order_by(SkillCategory.display_order, SkillCategory.name)
    )
    if only_active:
        cat_query = cat_query.where(SkillCategory.is_active == True)

    cat_result = await db.execute(cat_query)
    categories = cat_result.scalars().all()

    # Filter skills within categories if needed
    category_responses = []
    for cat in categories:
        skills = cat.skills if not only_active else [s for s in cat.skills if s.is_active]
        skills.sort(key=lambda s: (s.display_order, s.name))
        category_responses.append(
            SkillCategoryWithSkillsResponse(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                color=cat.color,
                icon=cat.icon,
                display_order=cat.display_order,
                is_active=cat.is_active,
                created_at=cat.created_at,
                updated_at=cat.updated_at,
                skills=[SkillResponse.model_validate(s) for s in skills],
            )
        )

    # Get uncategorized skills
    uncategorized_query = (
        select(Skill)
        .where(Skill.category_id == None)
        .order_by(Skill.display_order, Skill.name)
    )
    if only_active:
        uncategorized_query = uncategorized_query.where(Skill.is_active == True)

    uncategorized_result = await db.execute(uncategorized_query)
    uncategorized = uncategorized_result.scalars().all()

    return SkillCategoryListResponse(
        categories=category_responses,
        uncategorized=[SkillResponse.model_validate(s) for s in uncategorized],
    )


@router.get("/{skill_id}", response_model=SkillWithCategoryResponse)
async def get_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SkillWithCategoryResponse:
    """Get a single skill by ID."""
    query = (
        select(Skill)
        .options(selectinload(Skill.category))
        .where(Skill.id == skill_id)
    )
    result = await db.execute(query)
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return SkillWithCategoryResponse.model_validate(skill)


# ============ Admin Endpoints - Skills ============

@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> SkillResponse:
    """Create a new skill. Admin only."""
    # Generate slug if not provided
    slug = skill_data.slug or to_slug(skill_data.name)

    # Check for duplicate name or slug
    existing = await db.execute(
        select(Skill).where((Skill.name == skill_data.name) | (Skill.slug == slug))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill with this name or slug already exists",
        )

    # Verify category exists if provided
    if skill_data.category_id:
        cat_result = await db.execute(
            select(SkillCategory).where(SkillCategory.id == skill_data.category_id)
        )
        if not cat_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found",
            )

    skill = Skill(
        name=skill_data.name,
        slug=slug,
        description=skill_data.description,
        category_id=skill_data.category_id,
        display_order=skill_data.display_order,
        is_active=skill_data.is_active,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)

    return SkillResponse.model_validate(skill)


@router.patch("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: UUID,
    skill_data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> SkillResponse:
    """Update a skill. Admin only."""
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = skill_data.model_dump(exclude_unset=True)

    # Check for duplicate name if updating name
    if "name" in update_data and update_data["name"] != skill.name:
        existing = await db.execute(
            select(Skill).where(Skill.name == update_data["name"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill with this name already exists",
            )

    # Generate new slug if name changes and slug not provided
    if "name" in update_data and "slug" not in update_data:
        update_data["slug"] = to_slug(update_data["name"])

    # Check for duplicate slug if updating slug
    if "slug" in update_data and update_data["slug"] != skill.slug:
        existing = await db.execute(
            select(Skill).where(Skill.slug == update_data["slug"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill with this slug already exists",
            )

    # Verify category exists if updating category
    if "category_id" in update_data and update_data["category_id"]:
        cat_result = await db.execute(
            select(SkillCategory).where(SkillCategory.id == update_data["category_id"])
        )
        if not cat_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found",
            )

    for key, value in update_data.items():
        setattr(skill, key, value)

    await db.commit()
    await db.refresh(skill)

    return SkillResponse.model_validate(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> None:
    """Delete a skill. Admin only. Consider using is_active=false instead."""
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    await db.delete(skill)
    await db.commit()


# ============ Admin Endpoints - Categories ============

@router.get("/categories/", response_model=list[SkillCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> list[SkillCategoryResponse]:
    """List all skill categories."""
    query = select(SkillCategory).order_by(SkillCategory.display_order, SkillCategory.name)

    if not include_inactive or not current_user or not current_user.is_admin:
        query = query.where(SkillCategory.is_active == True)

    result = await db.execute(query)
    categories = result.scalars().all()

    return [SkillCategoryResponse.model_validate(c) for c in categories]


@router.post("/categories/", response_model=SkillCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: SkillCategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> SkillCategoryResponse:
    """Create a new skill category. Admin only."""
    # Check for duplicate name
    existing = await db.execute(
        select(SkillCategory).where(SkillCategory.name == category_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )

    category = SkillCategory(**category_data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return SkillCategoryResponse.model_validate(category)


@router.patch("/categories/{category_id}", response_model=SkillCategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: SkillCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> SkillCategoryResponse:
    """Update a skill category. Admin only."""
    result = await db.execute(
        select(SkillCategory).where(SkillCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_data.model_dump(exclude_unset=True)

    # Check for duplicate name if updating name
    if "name" in update_data and update_data["name"] != category.name:
        existing = await db.execute(
            select(SkillCategory).where(SkillCategory.name == update_data["name"])
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists",
            )

    for key, value in update_data.items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)

    return SkillCategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> None:
    """
    Delete a skill category. Admin only.
    Skills in this category will become uncategorized.
    """
    result = await db.execute(
        select(SkillCategory).where(SkillCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Set skills to uncategorized
    await db.execute(
        select(Skill).where(Skill.category_id == category_id)
    )
    skills_result = await db.execute(
        select(Skill).where(Skill.category_id == category_id)
    )
    skills = skills_result.scalars().all()
    for skill in skills:
        skill.category_id = None

    await db.delete(category)
    await db.commit()
