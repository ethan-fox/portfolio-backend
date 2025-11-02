from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class ContactView(BaseModel):
    """View model for contact responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
