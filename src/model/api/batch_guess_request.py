from pydantic import BaseModel

from src.model.api.guess_item import GuessItem


class BatchGuessRequest(BaseModel):
    """
    Request model for batch validation of multiple guesses.
    """
    guesses: list[GuessItem]
