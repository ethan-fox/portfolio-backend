class ApiKeyDAO:
    """Data Access Object for API key validation."""

    def __init__(self, allowed_keys: list[str]):
        """
        Initialize ApiKeyDAO with allowed API keys.

        Args:
            allowed_keys: List of valid API keys
        """
        self.allowed_keys = set(allowed_keys)

    def is_valid(self, api_key: str) -> bool:
        """
        Check if the provided API key is valid.

        Args:
            api_key: The API key to validate

        Returns:
            bool: True if the key is valid, False otherwise
        """
        return api_key in self.allowed_keys
