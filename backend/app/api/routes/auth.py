"""Authentication endpoints."""
from typing import Annotated

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_nonce,
    get_message_to_sign,
    verify_signature,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    NonceRequest,
    NonceResponse,
    TokenResponse,
    VerifyRequest,
)

router = APIRouter()

# In-memory nonce cache (TTL 5 minutes)
# In production, use Redis
nonce_cache: TTLCache = TTLCache(maxsize=10000, ttl=300)


@router.post("/nonce", response_model=NonceResponse)
async def get_nonce(request: NonceRequest) -> NonceResponse:
    """
    Get a nonce for wallet signature verification.
    
    Args:
        request: The nonce request containing wallet address
        
    Returns:
        The nonce and message to sign
    """
    wallet = request.wallet_address.lower()
    nonce = create_nonce()
    message = get_message_to_sign(nonce)
    
    # Store nonce for verification
    nonce_cache[wallet] = nonce
    
    return NonceResponse(nonce=nonce, message=message)


@router.post("/verify", response_model=TokenResponse)
async def verify_wallet(
    request: VerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Verify wallet signature and issue JWT token.
    
    Args:
        request: The verification request
        db: Database session
        
    Returns:
        Access token and user info
        
    Raises:
        HTTPException: If verification fails
    """
    wallet = request.wallet_address.lower()
    
    # Check nonce exists and matches
    stored_nonce = nonce_cache.get(wallet)
    if stored_nonce is None or stored_nonce != request.nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired nonce",
        )
    
    # Verify signature
    message = get_message_to_sign(request.nonce)
    if not verify_signature(wallet, message, request.signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )
    
    # Remove used nonce
    nonce_cache.pop(wallet, None)
    
    # Find or create user
    result = await db.execute(
        select(User).where(User.wallet_address == wallet)
    )
    user = result.scalar_one_or_none()
    
    is_new_user = False
    if user is None:
        # Create new user with minimal info
        user = User(
            wallet_address=wallet,
            name=f"User_{wallet[:8]}",
            country="NG",  # Default to Nigeria
        )
        db.add(user)
        await db.flush()
        is_new_user = True
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        is_new_user=is_new_user,
    )
