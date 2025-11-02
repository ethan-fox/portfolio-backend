from sqlalchemy.orm import Session
from uuid import UUID

from src.model.db.contact_orm import ContactORM


class ContactDAO:
    """Data Access Object for Contact entities."""

    def __init__(self, db: Session):
        """
        Initialize ContactDAO with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, contact: ContactORM) -> ContactORM:
        """
        Create a new contact in the database.

        Args:
            contact: ContactORM instance to create

        Returns:
            ContactORM: The created contact with generated ID
        """
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_by_id(self, contact_id: UUID) -> ContactORM | None:
        """
        Get a contact by ID.

        Args:
            contact_id: UUID of the contact

        Returns:
            ContactORM if found, None otherwise
        """
        return self.db.query(ContactORM).filter(ContactORM.id == contact_id).first()

    def get_all(self) -> list[ContactORM]:
        """
        Get all contacts from the database.

        Returns:
            List of ContactORM instances
        """
        return self.db.query(ContactORM).all()
