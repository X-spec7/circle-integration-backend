import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    app_name: str = Field(default="Token Investment Platform", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database settings
    database_url: str = Field(
        default=os.getenv("DB_URL", "postgresql://username:password@localhost:5432/database_name"),
        description="Database connection URL",
        alias="DB_URL"
    )
    
    # Security settings
    secret_key: str = Field(
        default=os.getenv("SECRET_KEY", "your-secret-key-here-change-this-in-production"),
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default=os.getenv("ALGORITHM", "HS256"), description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        description="Access token expiration time in minutes"
    )
    
    # Circle API settings
    circle_api_key: str = Field(
        default=os.getenv("CIRCLE_API_KEY", ""),
        description="Circle API key"
    )
    circle_base_url: str = Field(
        default=os.getenv("CIRCLE_BASE_URL", "https://api.circle.com/v1"),
        description="Circle API base URL"
    )
    # Note: Circle webhooks now use ECDSA signatures with public keys, not webhook secrets
    # The webhook_secret field is kept for backward compatibility but is no longer used
    circle_webhook_secret: str = Field(
        default=os.getenv("CIRCLE_WEBHOOK_SECRET", ""),
        description="Circle webhook secret (deprecated - now using ECDSA signatures)"
    )
    
    # Blockchain settings
    network: str = Field(
        default=os.getenv("NETWORK", "POLYGON"),
        description="Blockchain network"
    )
    polygon_rpc_url: str = Field(
        default=os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
        description="Polygon RPC URL"
    )
    polygon_private_key: str = Field(
        default=os.getenv("POLYGON_PRIVATE_KEY", ""),
        description="Private key for deploying contracts"
    )
    escrow_wallet_address: str = Field(
        default=os.getenv("ESCROW_WALLET_ADDRESS", ""),
        description="Default escrow wallet address"
    )
    
    # File upload settings
    upload_dir: str = Field(
        default=os.getenv("UPLOAD_DIR", "uploads"),
        description="File upload directory"
    )
    max_file_size: int = Field(
        default=int(os.getenv("MAX_FILE_SIZE", "10485760")),  # 10MB
        description="Maximum file size in bytes"
    )
    
    # CORS settings
    cors_origins: list = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # API settings
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings() 