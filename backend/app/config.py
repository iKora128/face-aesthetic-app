"""Application configuration using modern Pydantic v2 practices."""

import os
from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with modern Pydantic v2 configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Face Aesthetic API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    api_prefix: str = Field(default="/api/v1", description="API prefix")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto reload for development")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )
    cors_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods",
    )
    cors_headers: list[str] = Field(
        default=["*"], description="Allowed CORS headers"
    )

    # Security
    secret_key: str = Field(
        description="Secret key for JWT tokens",
        min_length=32,
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration minutes"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")

    # Supabase
    supabase_url: str = Field(description="Supabase project URL")
    supabase_key: str = Field(description="Supabase anon key")
    supabase_service_key: str = Field(description="Supabase service role key")

    # OpenAI
    openai_api_key: str = Field(description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4o-mini", description="OpenAI model for chat"
    )
    openai_max_tokens: int = Field(
        default=1000, description="Max tokens for OpenAI responses"
    )

    # LINE Bot
    line_channel_access_token: str | None = Field(
        default=None, description="LINE Bot channel access token"
    )
    line_channel_secret: str | None = Field(
        default=None, description="LINE Bot channel secret"
    )

    # File Upload
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="Max file size in bytes (10MB)"
    )
    allowed_image_types: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        description="Allowed image MIME types",
    )
    upload_dir: str = Field(default="uploads", description="Upload directory")

    # Analysis
    analysis_timeout: int = Field(
        default=30, description="Analysis timeout in seconds"
    )
    enable_gpu: bool = Field(default=False, description="Enable GPU acceleration")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        description="Log format",
    )

    # Redis (for caching and rate limiting)
    redis_url: str | None = Field(
        default=None, description="Redis URL for caching"
    )

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return not self.debug

    @computed_field  # type: ignore[misc]
    @property
    def upload_path(self) -> str:
        """Get absolute upload path."""
        return os.path.abspath(self.upload_dir)

    def get_supabase_config(self) -> dict[str, str]:
        """Get Supabase configuration dictionary."""
        return {
            "url": self.supabase_url,
            "key": self.supabase_key,
            "service_key": self.supabase_service_key,
        }

    def get_openai_config(self) -> dict[str, Any]:
        """Get OpenAI configuration dictionary."""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "max_tokens": self.openai_max_tokens,
        }

    def get_line_config(self) -> dict[str, str | None]:
        """Get LINE Bot configuration dictionary."""
        return {
            "access_token": self.line_channel_access_token,
            "channel_secret": self.line_channel_secret,
        }


class DevelopmentSettings(Settings):
    """Development environment settings."""

    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings."""

    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"


class TestingSettings(Settings):
    """Testing environment settings."""

    debug: bool = True
    testing: bool = True
    supabase_url: str = "http://localhost:54321"
    secret_key: str = "test-secret-key-for-testing-only-do-not-use-in-production"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings with caching."""
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export global settings instance
settings = get_settings()