from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class UserView(BaseModel):
    id: UUID
    google_id: str
    email: str
    name: str | None
    picture_url: str | None
    last_login_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
