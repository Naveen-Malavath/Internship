"""Configuration management for the AI Coding Agent"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration loaded from environment variables"""

    # OpenAI Settings
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", alias="OPENAI_MODEL")

    # Anthropic Settings
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022", alias="ANTHROPIC_MODEL"
    )

    # Default Provider
    default_llm_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")

    # Agent Settings
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    timeout_seconds: int = Field(default=300, alias="TIMEOUT_SECONDS")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Workspace
    workspace_path: Path = Field(default_factory=lambda: Path.cwd())

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the configuration singleton"""
    global _config
    if _config is None:
        # Load .env file
        load_dotenv()
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment"""
    global _config
    load_dotenv(override=True)
    _config = Config()
    return _config
