import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.fixture
async def second_user(db_session: AsyncSession) -> User:
    user = User(
        wallet_address="0xseconduser1234567890abcdef",
        name="Second User",
        country="UK",
        is_admin=False,
        is_banned=False,
        id_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_list_users_as_admin(
    client: AsyncClient,
    admin_headers: dict,
    test_user: User,
):
    response = await client.get("/api/admin/users", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_users_requires_admin(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/admin/users", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_filter_verified(
    client: AsyncClient,
    admin_headers: dict,
    second_user: User,
):
    response = await client.get(
        "/api/admin/users",
        headers=admin_headers,
        params={"verified": False},
    )
    
    assert response.status_code == 200
    data = response.json()
    for user in data["users"]:
        assert user["id_verified"] is False


@pytest.mark.asyncio
async def test_verify_user(
    client: AsyncClient,
    admin_headers: dict,
    second_user: User,
):
    response = await client.post(
        f"/api/admin/users/{second_user.id}/verify",
        headers=admin_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_verified"] is True


@pytest.mark.asyncio
async def test_verify_user_not_found(client: AsyncClient, admin_headers: dict):
    import uuid
    response = await client.post(
        f"/api/admin/users/{uuid.uuid4()}/verify",
        headers=admin_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ban_user(
    client: AsyncClient,
    admin_headers: dict,
    second_user: User,
):
    response = await client.post(
        f"/api/admin/users/{second_user.id}/ban",
        headers=admin_headers,
        json={"reason": "Violation of terms"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_banned"] is True


@pytest.mark.asyncio
async def test_ban_user_requires_reason(
    client: AsyncClient,
    admin_headers: dict,
    second_user: User,
):
    response = await client.post(
        f"/api/admin/users/{second_user.id}/ban",
        headers=admin_headers,
        json={},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_disputes_empty(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/admin/disputes", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "disputes" in data
    assert data["total"] >= 0
