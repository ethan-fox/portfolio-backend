from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    google_id: str
    email: str
    name: str | None
    picture_url: str | None
    last_login_at: datetime
    created_at: datetime
    updated_at: datetime
