from sqlalchemy import Column, String, Integer, Date, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.model.db.base import Base


class GuessrORM(Base):
    """
    Represents a daily guessr (puzzle set).
    One row per day.
    """
    __tablename__ = "guessr"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    puzzles = relationship("GuessrPuzzleORM", back_populates="guessr", cascade="all, delete-orphan")


class GuessrPuzzleORM(Base):
    """
    Represents an individual puzzle within a guessr.
    Three rows per guessr (puzzle_number: 0, 1, 2).
    """
    __tablename__ = "guessr_puzzle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guessr_id = Column(Integer, ForeignKey("guessr.id"), nullable=False, index=True)
    puzzle_number = Column(Integer, nullable=False)
    puzzle_type = Column(String, nullable=False)
    answer = Column(Integer, nullable=False)
    config = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    guessr = relationship("GuessrORM", back_populates="puzzles")

    __table_args__ = (
        UniqueConstraint('guessr_id', 'puzzle_number', name='uq_guessr_puzzle_number'),
    )
