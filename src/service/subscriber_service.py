from datetime import datetime, UTC

from src.dao.contact_dao import ContactDAO
from src.model.api.contact_request import ContactRequest
from src.model.view.contact_view import ContactView
from src.model.db.contact_orm import ContactORM


class SubscriberService:
    """Service for managing subscriber contacts."""

    def __init__(self, contact_dao: ContactDAO):
        """
        Initialize SubscriberService.

        Args:
            contact_dao: ContactDAO instance for database operations
        """
        self.contact_dao = contact_dao

    def store_signup(self, contact_data: ContactRequest) -> ContactView:
        """
        Store a new contact signup.

        Args:
            contact_data: Contact request data from API

        Returns:
            ContactView: The created contact as a view model
        """
        contact_orm = ContactORM(
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            phone=contact_data.phone,
            email=contact_data.email,
            created_at=datetime.now(UTC)
        )

        created_contact = self.contact_dao.create(contact_orm)

        return ContactView.model_validate(created_contact)

    def get_all_signups(self) -> list[ContactView]:
        """
        Get all contact signups.

        Returns:
            list[ContactView]: List of all contacts as view models
        """
        contacts_orm = self.contact_dao.get_all()

        return [ContactView.model_validate(contact) for contact in contacts_orm]
