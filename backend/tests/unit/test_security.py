"""Tests for security utilities."""
import pytest

from app.core.security import (
    create_access_token,
    create_nonce,
    decode_token,
    get_message_to_sign,
    verify_signature,
)


def test_create_nonce():
    """Test nonce creation."""
    nonce1 = create_nonce()
    nonce2 = create_nonce()
    
    assert len(nonce1) == 32  # 16 bytes = 32 hex chars
    assert nonce1 != nonce2


def test_get_message_to_sign():
    """Test message formatting."""
    nonce = "test-nonce-123"
    message = get_message_to_sign(nonce)
    
    assert "test-nonce-123" in message
    assert "Flow" in message


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    data = {"sub": "user-123"}
    token = create_access_token(data)
    
    decoded = decode_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert "exp" in decoded


def test_decode_invalid_token():
    """Test decoding invalid token."""
    result = decode_token("invalid-token")
    assert result is None


def test_verify_signature_invalid():
    """Test signature verification with invalid signature."""
    result = verify_signature(
        wallet_address="0x1234567890123456789012345678901234567890",
        message="test message",
        signature="0xinvalid",
    )
    assert result is False
