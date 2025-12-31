from pydantic import BaseModel, ConfigDict
from typing import Literal


class GuessrPuzzleView(BaseModel):
    """
    Response model for a single puzzle.
    NEVER exposes answer in GET response - only exposed in POST validation.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    puzzle_type: Literal["batting_stat", "pitching_stat", "award_votes", "starters"]
    hints: dict
    players: list[dict]
