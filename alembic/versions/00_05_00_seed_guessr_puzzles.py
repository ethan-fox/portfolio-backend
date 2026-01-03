"""seed_guessr_puzzles

Revision ID: 00_05_00
Revises: 00_04_00
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from alembic import op
from sqlalchemy.orm import Session

from src.dao.guessr_dao import GuessrDAO
from src.dao.baseball_csv_dao import BaseballCSVDAO
from src.service.guessr_service import GuessrService

# revision identifiers, used by Alembic.
revision: str = '00_05_00'
down_revision: Union[str, None] = '00_04_00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Seed the previous 7 days of puzzles in chronological order (oldest to newest).
    This ensures IDs are sequential and avoids out-of-order generation.
    """
    # Get database connection and create session
    bind = op.get_bind()
    session = Session(bind=bind)

    # Initialize DAOs and service
    guessr_dao = GuessrDAO(db=session)
    baseball_dao = BaseballCSVDAO()
    service = GuessrService(guessr_dao=guessr_dao, baseball_dao=baseball_dao)

    # Calculate date range (7 days ago through today, US Eastern time)
    eastern = ZoneInfo("America/New_York")
    today = date.today()  # Use server date for migration consistency

    # Generate puzzles for previous 7 days in chronological order
    for days_ago in range(7, 0, -1):  # 7, 6, 5, 4, 3, 2, 1
        puzzle_date = today - timedelta(days=days_ago)

        # Check if puzzles already exist for this date
        existing_guessr = guessr_dao.get_guessr_by_date(puzzle_date)
        if existing_guessr:
            print(f"Skipping {puzzle_date} - puzzles already exist")
            continue

        # Generate puzzles using service layer
        try:
            result = service.get_puzzles_for_date(puzzle_date)
            print(f"Generated puzzles for {puzzle_date} (guessr_id={result.id})")
        except Exception as e:
            print(f"Error generating puzzles for {puzzle_date}: {e}")
            # Continue with other dates even if one fails
            continue

    # Commit all changes
    session.commit()
    session.close()


def downgrade() -> None:
    """
    Remove seeded puzzles.
    Note: This deletes all guessr data, not just the seeded 7 days.
    """
    bind = op.get_bind()
    session = Session(bind=bind)

    # Delete all puzzle data (cascades to guessr_puzzle due to FK)
    session.execute("DELETE FROM guessr")
    session.commit()
    session.close()
