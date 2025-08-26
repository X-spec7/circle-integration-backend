import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    app_name: str = Field(default="FastAPI Backend", description="Application name")
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