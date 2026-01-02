from pydantic import BaseModel

from src.model.view.guess_validation_view import GuessValidationView


class BatchGuessValidationView(BaseModel):
    """
    Response model for POST /guessr/{guessr_id} - batch validation of all 3 puzzles.
    Contains individual validation results and an overall score.
    Overall score is the sum of individual scores plus 1 (range: 1-100).
    """
    results: list[GuessValidationView]
    overall_score: int
