from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class ContactRequest(BaseModel):
    """API request model for creating a contact."""

    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None

    @model_validator(mode='after')
    def check_contact_method(self):
        if not self.email and not self.phone:
            raise ValueError('At least one of email or phone must be provided')
        return self
