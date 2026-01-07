"""Integration tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_nonce(client: AsyncClient):
    """Test getting a nonce for wallet authentication."""
    response = await client.post(
        "/api/auth/nonce",
        json={"wallet_address": "0x1234567890123456789012345678901234567890"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "nonce" in data
    assert "message" in data
    assert len(data["nonce"]) == 32


@pytest.mark.asyncio
async def test_get_nonce_invalid_address(client: AsyncClient):
    """Test getting nonce with invalid wallet address."""
    response = await client.post(
        "/api/auth/nonce",
        json={"wallet_address": "invalid"},
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_invalid_nonce(client: AsyncClient):
    """Test verification with invalid nonce."""
    response = await client.post(
        "/api/auth/verify",
        json={
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "signature": "0x" + "0" * 130,
            "nonce": "invalid-nonce",
        },
    )
    
    assert response.status_code == 400
    assert "nonce" in response.json()["detail"].lower()
