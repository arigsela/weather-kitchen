"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""

import logging

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Insecure dev-only fallback — will trigger a warning at startup
_DEV_JWT_SECRET = "dev-secret-key-INSECURE-do-not-use-in-production-change-me"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Weather Kitchen API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # Database
    database_url: str = "sqlite:///./weather_kitchen.db"
    database_echo: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_general: int = 10  # requests per second
    rate_limit_pin_requests: int = 5  # per 15 minutes
    rate_limit_pin_window_minutes: int = 15

    # Logging
    log_level: str = "INFO"

    # Authentication & Authorization
    token_byte_length: int = 32  # 256 bits, encoded as urlsafe base64 = ~43 chars
    pin_min_length: int = 4
    pin_max_length: int = 6
    pin_max_attempts: int = 5
    pin_lockout_minutes: int = 15
    bcrypt_rounds: int = 12

    # Password settings
    password_min_length: int = 8
    password_max_length: int = 128
    password_max_attempts: int = 5
    password_lockout_minutes: int = 15

    # JWT Settings — JWT_SECRET_KEY must be set in production via environment variable
    jwt_secret_key: str = _DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Beta access gate (empty string = disabled, any value = required on login/signup)
    beta_access_code: str = ""

    # Pagination
    pagination_default_limit: int = 20
    pagination_max_limit: int = 100

    # Request validation
    request_body_size_limit_kb: int = 100  # 100KB max

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
