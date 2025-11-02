from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, UTC
import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.service.subscriber_service import SubscriberService
from src.dao.contact_dao import ContactDAO
from src.model.api.contact_request import ContactRequest
from src.model.view.contact_view import ContactView
from src.model.db.contact_orm import ContactORM


class TestSubscriberService:
    def setup_method(self):
        # Create mock DAO with spec for type safety
        self.mock_dao = MagicMock(spec=ContactDAO)
        # Instantiate service with mocked dependency
        self.service = SubscriberService(self.mock_dao)

    @patch('src.service.subscriber_service.datetime')
    def test_store_signup_with_email_only(self, mock_datetime):
        frozen_time = datetime(2025, 1, 15, 12, 30, 45, tzinfo=UTC)
        mock_datetime.now.return_value = frozen_time

        contact_request = ContactRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )

        mock_contact_id = uuid4()
        mock_contact_orm = ContactORM(
            id=mock_contact_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone=None,
            created_at=frozen_time
        )
        self.mock_dao.create.return_value = mock_contact_orm

        result = self.service.store_signup(contact_request)

        mock_datetime.now.assert_called_once_with(UTC)

        self.mock_dao.create.assert_called_once()
        created_orm = self.mock_dao.create.call_args[0][0]
        assert created_orm.first_name == "John"
        assert created_orm.last_name == "Doe"
        assert created_orm.email == "john.doe@example.com"
        assert created_orm.phone is None
        assert created_orm.created_at == frozen_time

        assert isinstance(result, ContactView)
        assert result.id == mock_contact_id
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john.doe@example.com"
        assert result.phone is None
        assert result.created_at == frozen_time

    @patch('src.service.subscriber_service.datetime')
    def test_store_signup_with_phone_only(self, mock_datetime):
        frozen_time = datetime(2025, 1, 15, 14, 20, 30, tzinfo=UTC)
        mock_datetime.now.return_value = frozen_time

        contact_request = ContactRequest(
            first_name="Jane",
            last_name="Smith",
            phone="+1-555-0123"
        )

        mock_contact_id = uuid4()
        mock_contact_orm = ContactORM(
            id=mock_contact_id,
            first_name="Jane",
            last_name="Smith",
            email=None,
            phone="+1-555-0123",
            created_at=frozen_time
        )
        self.mock_dao.create.return_value = mock_contact_orm

        result = self.service.store_signup(contact_request)

        mock_datetime.now.assert_called_once_with(UTC)

        self.mock_dao.create.assert_called_once()
        created_orm = self.mock_dao.create.call_args[0][0]
        assert created_orm.first_name == "Jane"
        assert created_orm.last_name == "Smith"
        assert created_orm.phone == "+1-555-0123"
        assert created_orm.email is None
        assert created_orm.created_at == frozen_time

        assert isinstance(result, ContactView)
        assert result.id == mock_contact_id
        assert result.first_name == "Jane"
        assert result.last_name == "Smith"
        assert result.phone == "+1-555-0123"
        assert result.email is None
        assert result.created_at == frozen_time

    @patch('src.service.subscriber_service.datetime')
    def test_store_signup_with_both_email_and_phone(self, mock_datetime):
        frozen_time = datetime(2025, 1, 15, 16, 45, 10, tzinfo=UTC)
        mock_datetime.now.return_value = frozen_time

        contact_request = ContactRequest(
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@example.com",
            phone="+1-555-9999"
        )

        mock_contact_id = uuid4()
        mock_contact_orm = ContactORM(
            id=mock_contact_id,
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@example.com",
            phone="+1-555-9999",
            created_at=frozen_time
        )
        self.mock_dao.create.return_value = mock_contact_orm

        result = self.service.store_signup(contact_request)

        mock_datetime.now.assert_called_once_with(UTC)

        self.mock_dao.create.assert_called_once()
        created_orm = self.mock_dao.create.call_args[0][0]
        assert created_orm.first_name == "Bob"
        assert created_orm.last_name == "Johnson"
        assert created_orm.email == "bob.johnson@example.com"
        assert created_orm.phone == "+1-555-9999"
        assert created_orm.created_at == frozen_time

        assert isinstance(result, ContactView)
        assert result.id == mock_contact_id
        assert result.first_name == "Bob"
        assert result.last_name == "Johnson"
        assert result.email == "bob.johnson@example.com"
        assert result.phone == "+1-555-9999"
        assert result.created_at == frozen_time

    def test_store_signup_raises_exception_on_db_failure(self):
        contact_request = ContactRequest(
            first_name="Error",
            last_name="Test",
            email="error@example.com"
        )

        self.mock_dao.create.side_effect = SQLAlchemyError("Database connection failed")

        with pytest.raises(SQLAlchemyError) as exc_info:
            self.service.store_signup(contact_request)

        assert "Database connection failed" in str(exc_info.value)
        self.mock_dao.create.assert_called_once()

    def test_get_all_signups_empty_list(self):
        self.mock_dao.get_all.return_value = []

        result = self.service.get_all_signups()

        self.mock_dao.get_all.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_all_signups_multiple_contacts(self):
        mock_contact_1_id = uuid4()
        mock_contact_2_id = uuid4()
        mock_created_at_1 = datetime.now(UTC)
        mock_created_at_2 = datetime.now(UTC)

        mock_contacts = [
            ContactORM(
                id=mock_contact_1_id,
                first_name="Alice",
                last_name="Williams",
                email="alice@example.com",
                phone=None,
                created_at=mock_created_at_1
            ),
            ContactORM(
                id=mock_contact_2_id,
                first_name="Charlie",
                last_name="Brown",
                email=None,
                phone="+1-555-1234",
                created_at=mock_created_at_2
            )
        ]
        self.mock_dao.get_all.return_value = mock_contacts

        result = self.service.get_all_signups()

        self.mock_dao.get_all.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 2

        assert isinstance(result[0], ContactView)
        assert result[0].id == mock_contact_1_id
        assert result[0].first_name == "Alice"
        assert result[0].last_name == "Williams"
        assert result[0].email == "alice@example.com"
        assert result[0].phone is None
        assert result[0].created_at == mock_created_at_1

        assert isinstance(result[1], ContactView)
        assert result[1].id == mock_contact_2_id
        assert result[1].first_name == "Charlie"
        assert result[1].last_name == "Brown"
        assert result[1].email is None
        assert result[1].phone == "+1-555-1234"
        assert result[1].created_at == mock_created_at_2

    def test_get_all_signups_raises_exception_on_db_failure(self):
        self.mock_dao.get_all.side_effect = SQLAlchemyError("Database query failed")

        with pytest.raises(SQLAlchemyError) as exc_info:
            self.service.get_all_signups()

        assert "Database query failed" in str(exc_info.value)
        self.mock_dao.get_all.assert_called_once()
