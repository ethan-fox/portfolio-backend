from unittest.mock import MagicMock

from src.service.auth_service import AuthService
from src.dao.api_key_dao import ApiKeyDAO


class TestAuthService:
    def setup_method(self):
        self.mock_dao = MagicMock(spec=ApiKeyDAO)
        self.service = AuthService(self.mock_dao)

    def test_validate_api_key_with_valid_key(self):
        self.mock_dao.is_valid.return_value = True

        result = self.service.validate_api_key("valid-key")

        assert result is True
        self.mock_dao.is_valid.assert_called_once_with("valid-key")

    def test_validate_api_key_with_invalid_key(self):
        self.mock_dao.is_valid.return_value = False

        result = self.service.validate_api_key("invalid-key")

        assert result is False
        self.mock_dao.is_valid.assert_called_once_with("invalid-key")

    def test_validate_api_key_with_none(self):
        result = self.service.validate_api_key(None)

        assert result is False
        self.mock_dao.is_valid.assert_not_called()

    def test_validate_api_key_with_empty_string(self):
        result = self.service.validate_api_key("")

        assert result is False
        self.mock_dao.is_valid.assert_not_called()
