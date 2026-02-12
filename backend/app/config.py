from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_title: str = "Mental Wellness API"
    api_version: str = "1.0.0"
    debug: bool = False

    secret_key: str = "change-me-in-production-use-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = "sqlite:///./mental_wellness.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    ai_provider: str = "mock"
    openai_api_key: str | None = None
    email_provider: str = "mock"
    sendgrid_api_key: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
