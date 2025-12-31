from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date

from src.model.db.guessr_orm import GuessrORM


class GuessrDAO:
    """Data Access Object for Guessr puzzles."""

    def __init__(self, db: Session):
        """
        Initialize GuessrDAO with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_puzzles_by_date(self, puzzle_date: date) -> list[GuessrORM]:
        """
        Get all 3 puzzles for a specific date.

        Args:
            puzzle_date: Date to query puzzles for

        Returns:
            List of GuessrORM instances ordered by puzzle_number
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.date == puzzle_date)\
            .order_by(GuessrORM.puzzle_number)\
            .all()

    def create_puzzle(self, puzzle: GuessrORM) -> GuessrORM:
        """
        Create a new puzzle in the database.
        Raises IntegrityError if duplicate (race condition).

        Args:
            puzzle: GuessrORM instance to create

        Returns:
            GuessrORM: The created puzzle

        Raises:
            IntegrityError: If unique constraint violated
        """
        try:
            self.db.add(puzzle)
            self.db.commit()
            self.db.refresh(puzzle)
            return puzzle
        except IntegrityError:
            self.db.rollback()
            raise

    def get_puzzle_by_id(self, puzzle_id: int) -> GuessrORM | None:
        """
        Get a puzzle by ID.

        Args:
            puzzle_id: Integer ID of the puzzle

        Returns:
            GuessrORM if found, None otherwise
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.id == puzzle_id)\
            .first()

    def get_puzzles_by_ids(self, puzzle_ids: list[int]) -> list[GuessrORM]:
        """
        Get multiple puzzles by their IDs (for batch validation).

        Args:
            puzzle_ids: List of puzzle integer IDs

        Returns:
            List of GuessrORM instances
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.id.in_(puzzle_ids))\
            .all()

    def get_puzzle_by_date_and_number(self, puzzle_date: date, puzzle_number: int) -> GuessrORM | None:
        """
        Get a specific puzzle by date and puzzle number.
        Used for race condition handling.

        Args:
            puzzle_date: Date of the puzzle
            puzzle_number: Puzzle number (0, 1, or 2)

        Returns:
            GuessrORM if found, None otherwise
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.date == puzzle_date)\
            .filter(GuessrORM.puzzle_number == puzzle_number)\
            .first()

    def get_puzzles_in_date_range(self, start_date: date, end_date: date) -> list[GuessrORM]:
        """
        Get all puzzles within a date range (for 365-day uniqueness check).

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of GuessrORM instances
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.date >= start_date)\
            .filter(GuessrORM.date <= end_date)\
            .all()
