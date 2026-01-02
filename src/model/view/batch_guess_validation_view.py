from pydantic import BaseModel

from src.model.view.guess_validation_view import GuessValidationView


class BatchGuessValidationView(BaseModel):
    """
    Response model for POST /guessr/{guessr_id} - batch validation response.
    Contains individual validation results and overall score across all puzzles.
    Overall score ranges from 1 (minimum) to 100 (maximum, all correct).
    Formula: sum(puzzle scores) + 1
    """
    results: list[GuessValidationView]
    overall_score: int
