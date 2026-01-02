from pydantic import BaseModel, field_validator


class GuessItem(BaseModel):
    """
    Request model for a single guess in batch validation.
    'id' represents the puzzle_number (0, 1, or 2).
    """
    id: int
    year: int

    @field_validator('id')
    def validate_puzzle_number(cls, v):
        if v < 0 or v > 2:
            raise ValueError('Puzzle number must be between 0 and 2')
        return v

    @field_validator('year')
    def validate_year_range(cls, v):
        if v < 1947 or v > 2024:
            raise ValueError('Year must be between 1947 and 2024')
        return v
