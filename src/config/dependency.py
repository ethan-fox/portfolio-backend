from functools import lru_cache
from sqlalchemy.orm import Session
from typing import Generator

from src.config.settings import get_settings
from src.util.database_manager import DatabaseManager

settings = get_settings()


@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Get the singleton database manager instance."""
    return DatabaseManager(
        database_url=settings.database_url,
        quiet=settings.environment != "LOCAL"  # Verbose in LOCAL, quiet in PROD
    )


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    manager = get_database_manager()
    yield from manager.get_session()
