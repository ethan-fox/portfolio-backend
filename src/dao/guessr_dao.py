from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime

from src.model.db.guessr_orm import GuessrORM, GuessrPuzzleORM


class GuessrDAO:
    """Data Access Object for Guessr and GuessrPuzzle entities."""

    def __init__(self, db: Session):
        """
        Initialize GuessrDAO with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_guessr(self, puzzle_date: date, created_at: datetime) -> GuessrORM:
        """
        Create a new guessr (daily puzzle set) for a given date.

        Args:
            puzzle_date: Date for the guessr
            created_at: Timestamp for creation

        Returns:
            GuessrORM: The created guessr with its ID

        Raises:
            IntegrityError: If guessr for this date already exists
        """
        guessr = GuessrORM(date=puzzle_date, created_at=created_at)
        self.db.add(guessr)
        self.db.flush()  # Get the ID without committing
        return guessr

    def get_guessr_by_id(self, guessr_id: int) -> GuessrORM | None:
        """
        Get a guessr by its ID.

        Args:
            guessr_id: Integer ID of the guessr

        Returns:
            GuessrORM if found, None otherwise
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.id == guessr_id)\
            .first()

    def get_guessr_by_date(self, puzzle_date: date) -> GuessrORM | None:
        """
        Get a guessr by its date.

        Args:
            puzzle_date: Date of the guessr

        Returns:
            GuessrORM if found, None otherwise
        """
        return self.db.query(GuessrORM)\
            .filter(GuessrORM.date == puzzle_date)\
            .first()

    def get_all_guessrs(self) -> list[GuessrORM]:
        """
        Get all guessrs ordered by date descending (newest first).

        Returns:
            List of all GuessrORM instances
        """
        return self.db.query(GuessrORM)\
            .order_by(GuessrORM.date.desc())\
            .all()

    def create_puzzle(self, puzzle: GuessrPuzzleORM) -> GuessrPuzzleORM:
        """
        Create a new puzzle for a guessr.

        Args:
            puzzle: GuessrPuzzleORM instance to create

        Returns:
            GuessrPuzzleORM: The created puzzle

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

    def get_puzzles_by_guessr_id(self, guessr_id: int) -> list[GuessrPuzzleORM]:
        """
        Get all puzzles (should be 3) for a guessr.

        Args:
            guessr_id: Integer ID of the guessr

        Returns:
            List of GuessrPuzzleORM instances ordered by puzzle_number
        """
        return self.db.query(GuessrPuzzleORM)\
            .filter(GuessrPuzzleORM.guessr_id == guessr_id)\
            .order_by(GuessrPuzzleORM.puzzle_number)\
            .all()

    def get_puzzle_by_guessr_and_number(self, guessr_id: int, puzzle_number: int) -> GuessrPuzzleORM | None:
        """
        Get a specific puzzle by guessr ID and puzzle number.
        Used for race condition handling.

        Args:
            guessr_id: Integer ID of the guessr
            puzzle_number: Puzzle number (0, 1, or 2)

        Returns:
            GuessrPuzzleORM if found, None otherwise
        """
        return self.db.query(GuessrPuzzleORM)\
            .filter(GuessrPuzzleORM.guessr_id == guessr_id)\
            .filter(GuessrPuzzleORM.puzzle_number == puzzle_number)\
            .first()

    def get_puzzles_in_date_range(self, start_date: date, end_date: date) -> list[GuessrPuzzleORM]:
        """
        Get all puzzles within a date range (for 365-day uniqueness check).

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of GuessrPuzzleORM instances
        """
        return self.db.query(GuessrPuzzleORM)\
            .join(GuessrORM)\
            .filter(GuessrORM.date >= start_date)\
            .filter(GuessrORM.date <= end_date)\
            .all()
