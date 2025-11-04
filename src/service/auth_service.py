from src.dao.api_key_dao import ApiKeyDAO


class AuthService:
    """Service for authentication and authorization operations."""

    def __init__(self, api_key_dao: ApiKeyDAO):
        """
        Initialize AuthService.

        Args:
            api_key_dao: ApiKeyDAO instance for API key validation
        """
        self.api_key_dao = api_key_dao

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key.

        Args:
            api_key: The API key to validate

        Returns:
            bool: True if the API key is valid, False otherwise
        """
        if not api_key:
            return False
        return self.api_key_dao.is_valid(api_key)
