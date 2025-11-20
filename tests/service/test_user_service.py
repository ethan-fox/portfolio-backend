from datetime import datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4
from src.service.user_service import UserService
from src.dao.user_dao import UserDAO
from src.model.db.user_orm import UserORM
from src.model.view.user_view import UserView


class TestUserService:
    def setup_method(self):
        self.mock_dao = MagicMock(spec=UserDAO)
        self.service = UserService(self.mock_dao)

    def test_authenticate_user_creates_new_user(self):
        self.mock_dao.find_by_google_id.return_value = None

        mock_dt = datetime.now()
        mock_user = UserORM(
            id=uuid4(),
            google_id="google_123",
            email="test@example.com",
            name="Test User",
            picture_url="https://example.com/pic.jpg",
            last_login_at=mock_dt,
            created_at=mock_dt,
            updated_at=mock_dt,
        )
        self.mock_dao.create.return_value = mock_user

        result = self.service.authenticate_user(
            "google_123", "test@example.com", "Test User", "https://example.com/pic.jpg"
        )

        self.mock_dao.find_by_google_id.assert_called_once_with("google_123")
        self.mock_dao.create.assert_called_once()
        self.mock_dao.update_profile_and_login.assert_not_called()
        assert isinstance(result, UserView)
        assert result.google_id == "google_123"

    def test_authenticate_user_updates_existing_user(self):
        test_uuid = uuid4()
        mock_dt = datetime.now()
        mock_existing = UserORM(
            id=test_uuid,
            google_id="google_123",
            email="old@example.com",
            last_login_at=mock_dt,
            created_at=mock_dt,
            updated_at=mock_dt,
        )
        self.mock_dao.find_by_google_id.return_value = mock_existing

        mock_update_dt = mock_dt + timedelta(seconds=5)
        mock_updated = UserORM(
            id=test_uuid,
            google_id="google_123",
            email="new@example.com",
            last_login_at=mock_update_dt,
            created_at=mock_update_dt,
            updated_at=mock_dt,
        )
        self.mock_dao.update_profile_and_login.return_value = mock_updated

        result = self.service.authenticate_user(
            "google_123", "new@example.com", "Test User", "https://example.com/pic.jpg"
        )

        self.mock_dao.update_profile_and_login.assert_called_once()
        self.mock_dao.create.assert_not_called()
        assert isinstance(result, UserView)
        assert result.email == "new@example.com"
