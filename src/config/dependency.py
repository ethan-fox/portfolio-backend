from functools import lru_cache
from sqlalchemy.orm import Session
from typing import Generator
from fastapi import Depends

from src.config.settings import get_settings
from src.util.database_manager import DatabaseManager
from src.dao.contact_dao import ContactDAO
from src.service.subscriber_service import SubscriberService

settings = get_settings()


@lru_cache()
def get_database_manager() -> DatabaseManager:
    return DatabaseManager(
        database_url=settings.database_url,
        quiet=settings.environment != "LOCAL"
    )


def get_db() -> Generator[Session, None, None]:
    manager = get_database_manager()
    yield from manager.get_session()


def get_contact_dao(db: Session = Depends(get_db)) -> ContactDAO:
    return ContactDAO(db)


def get_subscriber_service(dao: ContactDAO = Depends(get_contact_dao)) -> SubscriberService:
    return SubscriberService(dao)
