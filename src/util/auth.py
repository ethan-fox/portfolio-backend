from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader

from src.service.auth_service import AuthService
from src.config.dependency import get_auth_service

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    api_key: str = Security(api_key_header),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """FastAPI dependency for API key authentication."""
    if not auth_service.validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )
    return api_key
