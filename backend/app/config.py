from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    api_title: str = "MindfulPath API"
    api_version: str = "2.0.0"
    debug: bool = False

    # In-house JWT (legacy, kept for backward compat)
    secret_key: str = "change-me-in-production-use-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    # Database
    database_url: str = "sqlite:///./mental_wellness.db"

    # CORS – comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Clerk authentication
    # Set CLERK_PUBLISHABLE_KEY in .env (starts with pk_...)
    # Set CLERK_JWKS_URL to: https://<your-clerk-domain>/.well-known/jwks.json
    clerk_jwks_url: Optional[str] = None

    # AI backend
    ai_provider: str = "mock"
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
