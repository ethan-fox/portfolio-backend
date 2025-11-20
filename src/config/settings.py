from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    PROD = "PROD"


class Settings(BaseSettings):
    environment: Environment = Environment.LOCAL
    database_url: str
    google_cloud_project: str = "portfolio-477017"
    google_oauth_client_id: str

    api_title: str = "Portfolio API"
    api_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
