from sqlalchemy import Column, String, Integer, Date, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from src.model.db.base import Base


class GuessrORM(Base):
    __tablename__ = "guessr"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    puzzle_number = Column(Integer, nullable=False)
    puzzle_type = Column(String, nullable=False)
    answer = Column(Integer, nullable=False)
    config = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint('date', 'puzzle_number', name='uq_guessr_date_puzzle_number'),
    )
