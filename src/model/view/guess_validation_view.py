from pydantic import BaseModel


class GuessValidationView(BaseModel):
    """
    Response model for POST /guessr/{date} - validation result for a single guess.
    Reveals the correct answer for comparison.
    """
    id: int
    valid: bool
    correct_answer: int
