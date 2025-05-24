"""
Application configuration settings.

This module contains all configuration settings for the PlaybookWiz API,
using Pydantic settings for validation and environment variable loading.
"""

import secrets
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "PlaybookWiz API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # API
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str
    MONGODB_URL: str
    REDIS_URL: str

    # AI/ML
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"

    # Vector Database
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "playbookwiz-embeddings"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 104857600  # 100MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "ppt", "pptx", "doc", "docx"]

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600

    # CORS
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # External APIs
    GOOGLE_API_KEY: Optional[str] = None
    SERP_API_KEY: Optional[str] = None

    # Selenium
    SELENIUM_DRIVER_PATH: str = "/usr/local/bin/chromedriver"
    SELENIUM_HEADLESS: bool = True

    # spaCy
    SPACY_MODEL: str = "en_core_web_sm"

    # Cache
    CACHE_TTL: int = 3600

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Assemble CORS origins from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("ALLOWED_EXTENSIONS", pre=True)
    def assemble_allowed_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        """Assemble allowed file extensions from environment variable."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("ALLOWED_METHODS", pre=True)
    def assemble_allowed_methods(cls, v: Union[str, List[str]]) -> List[str]:
        """Assemble allowed HTTP methods from environment variable."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
