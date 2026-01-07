"""Application configuration using pydantic-settings."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "Flow API"
    debug: bool = False
    api_v1_prefix: str = "/api"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flow"
    database_echo: bool = False
    
    # Security
    jwt_secret: str = "change-this-in-production-use-256-bit-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # Blockchain
    base_rpc_url: str = "https://sepolia.base.org"
    escrow_contract_address: Optional[str] = None
    registry_contract_address: Optional[str] = None
    admin_wallet: Optional[str] = None
    
    # External Services
    claude_api_key: Optional[str] = None
    pinata_api_key: Optional[str] = None
    pinata_secret: Optional[str] = None
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
