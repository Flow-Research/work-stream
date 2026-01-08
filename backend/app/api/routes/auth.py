from typing import Annotated

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter, RATE_LIMIT_AUTH
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
@limiter.limit(RATE_LIMIT_AUTH)
async def get_nonce(request: Request, body: NonceRequest) -> NonceResponse:
    wallet = body.wallet_address.lower()
    nonce = create_nonce()
    message = get_message_to_sign(nonce)
    
    # Store nonce for verification
    nonce_cache[wallet] = nonce
    
    return NonceResponse(nonce=nonce, message=message)


@router.post("/verify", response_model=TokenResponse)
@limiter.limit(RATE_LIMIT_AUTH)
async def verify_wallet(
    request: Request,
    body: VerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    wallet = body.wallet_address.lower()
    
    stored_nonce = nonce_cache.get(wallet)
    if stored_nonce is None or stored_nonce != body.nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired nonce",
        )
    
    message = get_message_to_sign(body.nonce)
    if not verify_signature(wallet, message, body.signature):
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
