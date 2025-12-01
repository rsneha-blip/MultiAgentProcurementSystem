"""
Configuration settings for the Procurement AI Agents system.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.1", env="OPENAI_MODEL")
    
    # MCP Server Configuration
    mcp_server_port: int = Field(default=8000, env="MCP_SERVER_PORT")
    mcp_server_host: str = Field(default="localhost", env="MCP_SERVER_HOST")
    
    # Application Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug_mode: bool = Field(default=True, env="DEBUG_MODE")
    
    # Session Configuration
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")  # 1 hour
    max_sessions: int = Field(default=100, env="MAX_SESSIONS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings