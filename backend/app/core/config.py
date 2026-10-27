from typing import List, Optional
import os
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "MarketLab AI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "marketlab-super-secret-key-change-in-production-32chars"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./marketlab.db"
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Providers
    LLM_PROVIDER: str = "mock"  # mock, openai, gemini
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Embeddings
    EMBEDDING_PROVIDER: str = "mock"  # mock, openai, gemini
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536

    # Market Data
    MARKET_DATA_PROVIDER: str = "fixture"  # fixture, nse_bse

    # Security & Internal Tokens
    API_KEY_ENABLED: bool = False
    API_KEY: str = "marketlab-test-key"
    INTERNAL_AUTOMATION_TOKEN: str = "marketlab-internal-automation-token-secure"

    # Worker & Execution
    RESEARCH_TIMEOUT_SECONDS: int = 300
    MAX_AGENT_RETRIES: int = 2


settings = Settings()
