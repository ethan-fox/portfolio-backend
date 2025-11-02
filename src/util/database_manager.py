from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator


class DatabaseManager:
    """
    Database manager that handles SQLAlchemy engine, sessions, and ORM base.
    Provides connection pooling and session management.
    """

    def __init__(self, database_url: str, quiet: bool = False):
        """
        Initialize the database manager.

        Args:
            database_url: PostgreSQL connection string
            quiet: If True, suppress SQL logging. If False, log SQL statements.
        """
        self.database_url = database_url

        # Single engine instance with connection pooling
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,         # Max connections in pool
            max_overflow=10,     # Max overflow connections
            echo=not quiet       # Invert quiet to get echo value
        )

        # Session factory (private)
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Base class for ORM models
        self.Base = declarative_base()

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
