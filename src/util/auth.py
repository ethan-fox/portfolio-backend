from fastapi import Security, HTTPException, status, Depends, Request
from fastapi.security import APIKeyHeader

from src.service.auth_service import AuthService
from src.config.dependency import get_auth_service
from src.config.settings import get_settings, Environment

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
settings = get_settings()


def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """FastAPI dependency for API key authentication.

    In LOCAL environment, browser requests from localhost:5173 bypass API key check.
    In PROD environment, all requests require valid API key.
    """
    if settings.environment == Environment.LOCAL:
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if origin and origin == "http://localhost:5173":
            return "browser_bypass"
        if referer and referer.startswith("http://localhost:5173"):
            return "browser_bypass"

    if not auth_service.validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )
    return api_key
