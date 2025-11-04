from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"


class Settings(BaseSettings):
    environment: Environment = Environment.LOCAL
    database_url: str
    api_key: str

    api_title: str = "Portfolio API"
    api_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Dependency function to get cached settings instance."""
    return Settings()
