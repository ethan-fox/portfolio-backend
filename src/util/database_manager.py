from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator


class DatabaseManager:
    """
    Database manager that handles SQLAlchemy engine and session management.
    Provides connection pooling and session lifecycle management.
    """

    def __init__(self, database_url: str, quiet: bool = False):
        """
        Initialize the database manager.

        Args:
            database_url: PostgreSQL connection string
            quiet: If True, suppress SQL logging. If False, log SQL statements.
        """
        self.database_url = database_url

        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=not quiet
        )

        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _get_session(self) -> Session:
        """
        Create and return a new database session from the session factory.

        Returns:
            Session: A new SQLAlchemy session
        """
        return self._session_factory()

    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session (for use with FastAPI Depends).
        Automatically closes the session after use.

        Yields:
            Session: A database session that is automatically closed
        """
        session = self._get_session()
        try:
            yield session
        finally:
            session.close()
