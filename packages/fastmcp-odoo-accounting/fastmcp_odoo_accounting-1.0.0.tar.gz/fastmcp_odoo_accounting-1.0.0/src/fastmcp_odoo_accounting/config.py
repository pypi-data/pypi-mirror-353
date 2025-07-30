"""Configuration management for Odoo MCP server."""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Server configuration from environment variables."""
    
    # Odoo connection settings
    odoo_url: str = Field(..., description="Odoo server URL")
    odoo_db: str = Field(..., description="Odoo database name")
    odoo_user: str = Field(..., description="Odoo username/email")
    odoo_api_key: str = Field(..., description="Odoo API key")
    
    # MCP server settings
    mcp_host: str = Field(default="0.0.0.0", description="Host to bind to")
    mcp_port: int = Field(default=8001, description="Port to bind to")
    mcp_transport: str = Field(default="streamable-http", description="MCP transport type")
    
    # JWT authentication (optional)
    jwt_public_key_pem: Optional[str] = Field(default=None, description="Base64-encoded PEM public key")
    jwt_issuer: Optional[str] = Field(default=None, description="JWT issuer URL")
    jwt_audience: Optional[str] = Field(default="odoo-accounting-mcp", description="JWT audience")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    @field_validator("odoo_url")
    def validate_odoo_url(cls, v: str) -> str:
        """Ensure Odoo URL is properly formatted."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Odoo URL must start with http:// or https://")
        return v.rstrip("/")
    
    @field_validator("mcp_transport")
    def validate_transport(cls, v: str) -> str:
        """Validate transport type."""
        valid_transports = ["streamable-http", "sse", "stdio"]
        if v not in valid_transports:
            raise ValueError(f"Transport must be one of {valid_transports}")
        return v
    
    @field_validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode (with JWT auth)."""
        return self.jwt_public_key_pem is not None
    
    model_config = {
        "env_prefix": "",
        "case_sensitive": False,
        "extra": "ignore"
    }


def load_config() -> Config:
    """Load configuration from environment variables."""
    # Try to load from .env file if it exists (dev convenience)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Create config from environment
    return Config(
        odoo_url=os.environ.get("ODOO_URL", ""),
        odoo_db=os.environ.get("ODOO_DB", ""),
        odoo_user=os.environ.get("ODOO_USER", ""),
        odoo_api_key=os.environ.get("ODOO_API_KEY", ""),
        mcp_host=os.environ.get("MCP_HOST", "0.0.0.0"),
        mcp_port=int(os.environ.get("MCP_PORT", "8001")),
        mcp_transport=os.environ.get("MCP_TRANSPORT", "streamable-http"),
        jwt_public_key_pem=os.environ.get("JWT_PUBLIC_KEY_PEM"),
        jwt_issuer=os.environ.get("JWT_ISSUER"),
        jwt_audience=os.environ.get("JWT_AUDIENCE", "odoo-accounting-mcp"),
        log_level=os.environ.get("LOG_LEVEL", "INFO")
    )