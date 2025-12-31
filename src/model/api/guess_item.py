from pydantic import BaseModel, field_validator


class GuessItem(BaseModel):
    """
    Request model for a single guess in batch validation.
    """
    id: int
    year: int

    @field_validator('year')
    def validate_year_range(cls, v):
        if v < 1947 or v > 2024:
            raise ValueError('Year must be between 1947 and 2024')
        return v
