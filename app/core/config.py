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
    circle_webhook_secret: str = Field(
        default=os.getenv("CIRCLE_WEBHOOK_SECRET", ""),
        description="Circle webhook secret (deprecated - now using ECDSA signatures)"
    )
    circle_mint_wallet_id: str = Field(
        default=os.getenv("CIRCLE_MINT_WALLET_ID", ""),
        description="Circle Mint wallet ID for crypto payouts"
    )
    
    # Blockchain settings
    network: str = Field(
        default=os.getenv("NETWORK", "SEPOLIA"),
        description="Blockchain network (SEPOLIA, POLYGON, MAINNET)"
    )
    
    # Sepolia testnet settings
    sepolia_rpc_url: str = Field(
        default=os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_PROJECT_ID"),
        description="Sepolia RPC URL"
    )
    sepolia_private_key: str = Field(
        default=os.getenv("SEPOLIA_WALLET_PRIVATE_KEY", ""),
        description="Private key for deploying contracts on Sepolia"
    )
    
    # Polygon settings
    polygon_rpc_url: str = Field(
        default=os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
        description="Polygon RPC URL"
    )
    polygon_private_key: str = Field(
        default=os.getenv("POLYGON_PRIVATE_KEY", ""),
        description="Private key for deploying contracts on Polygon"
    )
    
    # Ethereum mainnet settings
    mainnet_rpc_url: str = Field(
        default=os.getenv("MAINNET_RPC_URL", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"),
        description="Ethereum mainnet RPC URL"
    )
    mainnet_private_key: str = Field(
        default=os.getenv("MAINNET_PRIVATE_KEY", ""),
        description="Private key for deploying contracts on mainnet"
    )
    
    # Legacy settings (for backward compatibility)
    escrow_wallet_address: str = Field(
        default=os.getenv("ESCROW_WALLET_ADDRESS", ""),
        description="Default escrow wallet address (legacy)"
    )
    sepolia_wallet_private_key: str = Field(
        default=os.getenv("SEPOLIA_WALLET_PRIVATE_KEY", ""),
        description="Sepolia wallet private key (legacy)"
    )
    sepolia_wallet_public_key: str = Field(
        default=os.getenv("SEPOLIA_WALLET_PUBLIC_KEY", ""),
        description="Sepolia wallet public key (legacy)"
    )
    
    # Network-specific settings
    @property
    def rpc_url(self) -> str:
        """Get RPC URL based on selected network"""
        if self.network.upper() == "SEPOLIA":
            return self.sepolia_rpc_url
        elif self.network.upper() == "POLYGON":
            return self.polygon_rpc_url
        elif self.network.upper() == "MAINNET":
            return self.mainnet_rpc_url
        else:
            return self.sepolia_rpc_url  # Default to Sepolia
    
    @property
    def private_key(self) -> str:
        """Get private key based on selected network"""
        if self.network.upper() == "SEPOLIA":
            return self.sepolia_private_key or self.sepolia_wallet_private_key
        elif self.network.upper() == "POLYGON":
            return self.polygon_private_key
        elif self.network.upper() == "MAINNET":
            return self.mainnet_private_key
        else:
            return self.sepolia_private_key or self.sepolia_wallet_private_key  # Default to Sepolia
    
    @property
    def usdc_address(self) -> str:
        """Get USDC address based on selected network"""
        if self.network.upper() == "SEPOLIA":
            return "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"  # Sepolia USDC
        elif self.network.upper() == "POLYGON":
            return "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # Polygon USDC
        elif self.network.upper() == "MAINNET":
            return "0xA0b86a33E6441b8c4C8C0d4b0c8C0d4b0c8C0d4b"  # Mainnet USDC
        else:
            return "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"  # Default to Sepolia
    
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
        extra = "ignore"  # Ignore extra fields

# Global settings instance
settings = Settings()
