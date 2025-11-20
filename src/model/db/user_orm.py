from sqlalchemy import Column, UUID, String, Text, TIMESTAMP
from sqlalchemy.sql import func
import uuid

from src.model.db.base import Base

class UserORM(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    picture_url = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    last_login_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)