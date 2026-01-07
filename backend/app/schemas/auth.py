"""Authentication schemas."""
from pydantic import BaseModel, Field


class NonceRequest(BaseModel):
    """Request schema for getting a nonce."""
    
    wallet_address: str = Field(
        ...,
        min_length=42,
        max_length=42,
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="Ethereum wallet address",
    )


class NonceResponse(BaseModel):
    """Response schema for nonce."""
    
    nonce: str = Field(..., description="Random nonce to sign")
    message: str = Field(..., description="Full message to sign")


class VerifyRequest(BaseModel):
    """Request schema for verifying a signed message."""
    
    wallet_address: str = Field(
        ...,
        min_length=42,
        max_length=42,
        pattern=r"^0x[a-fA-F0-9]{40}$",
    )
    signature: str = Field(..., description="Signature of the nonce message")
    nonce: str = Field(..., description="The nonce that was signed")


class TokenResponse(BaseModel):
    """Response schema for authentication token."""
    
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_new_user: bool = False


class RefreshRequest(BaseModel):
    """Request schema for refreshing a token."""
    
    refresh_token: str
