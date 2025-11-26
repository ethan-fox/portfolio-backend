from functools import lru_cache
from sqlalchemy.orm import Session
from typing import Generator
from fastapi import Depends

from src.config.settings import get_settings
from src.dao.user_dao import UserDAO
from src.service.user_service import UserService
from src.service.content_service import ContentService
from src.util.database_manager import DatabaseManager
from src.dao.contact_dao import ContactDAO
from src.service.subscriber_service import SubscriberService

settings = get_settings()


@lru_cache()
def get_database_manager() -> DatabaseManager:
    return DatabaseManager(
        database_url=settings.database_url,
        quiet=settings.environment != "LOCAL",  # TODO extract this to settings?
    )


def get_db() -> Generator[Session, None, None]:
    manager = get_database_manager()
    yield from manager.get_session()


def get_contact_dao(db: Session = Depends(get_db)) -> ContactDAO:
    return ContactDAO(db)


def get_user_dao(db: Session = Depends(get_db)) -> UserDAO:
    return UserDAO(db)


def get_user_service(user_dao: UserDAO = Depends(get_user_dao)) -> UserService:
    return UserService(user_dao)


def get_subscriber_service(
    dao: ContactDAO = Depends(get_contact_dao),
) -> SubscriberService:
    return SubscriberService(dao)


def get_content_service() -> ContentService:
    return ContentService()
