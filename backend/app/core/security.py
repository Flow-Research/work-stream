"""Security utilities for authentication and authorization."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from eth_account.messages import encode_defunct
from jose import JWTError, jwt
from web3 import Web3

from app.core.config import settings


def create_nonce() -> str:
    """Create a random nonce for wallet signature verification."""
    import secrets
    return secrets.token_hex(16)


def verify_signature(wallet_address: str, message: str, signature: str) -> bool:
    """
    Verify that a message was signed by the given wallet address.
    
    Args:
        wallet_address: The Ethereum wallet address
        message: The message that was signed
        signature: The signature to verify
        
    Returns:
        True if the signature is valid, False otherwise
    """
    try:
        w3 = Web3()
        message_hash = encode_defunct(text=message)
        recovered_address = w3.eth.account.recover_message(
            message_hash, signature=signature
        )
        return recovered_address.lower() == wallet_address.lower()
    except Exception:
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def get_message_to_sign(nonce: str) -> str:
    """
    Get the message format for wallet signature verification.
    
    Args:
        nonce: The unique nonce for this authentication attempt
        
    Returns:
        The formatted message to sign
    """
    return f"Sign this message to authenticate with Flow.\n\nNonce: {nonce}"
