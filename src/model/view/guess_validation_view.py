from pydantic import BaseModel


class GuessValidationView(BaseModel):
    """
    Response model for POST /guessr/{date} - validation result for a single guess.
    Reveals the correct answer for comparison and calculates score based on accuracy.
    Score ranges from 0-33 points using exponential decay formula.
    """
    id: int
    valid: bool
    correct_answer: int
    score: int
