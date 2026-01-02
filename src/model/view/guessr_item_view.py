from pydantic import BaseModel


class GuessrItemView(BaseModel):
    """
    Response model for listing available guessrs.
    Contains just the ID and date for each guessr.
    """
    id: int
    date: str
