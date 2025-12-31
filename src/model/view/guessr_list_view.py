from pydantic import BaseModel

from src.model.view.guessr_puzzle_view import GuessrPuzzleView


class GuessrListView(BaseModel):
    """
    Response model for GET /guessr?date={date} - returns guessr with 3 puzzles.
    The id represents the guessr (the daily puzzle set).
    """
    id: int
    date: str
    puzzles: list[GuessrPuzzleView]
