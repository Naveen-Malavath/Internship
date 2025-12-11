from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "AutoAgents Demo Backend"
    PROJECT_VERSION: str = "1.0.0"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./autoagents.db"
    ECHO_SQL: bool = False
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()

