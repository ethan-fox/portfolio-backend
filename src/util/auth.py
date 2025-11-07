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
    """FastAPI dependency for authentication.

    LOCAL: No authentication required.
    PROD: Accept either valid API key OR valid load balancer headers.
    """
    if settings.environment == Environment.LOCAL:
        return "local_bypass"

    if _is_valid_load_balancer_request(request):
        return "lb_authenticated"

    if auth_service.validate_api_key(api_key):
        return api_key

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid authentication: requires API key or load balancer headers"
    )


def _is_valid_load_balancer_request(request: Request) -> bool:
    """Validate request came through GCP Load Balancer.

    Checks for GCP-specific headers that indicate traffic from Load Balancer.
    """
    via = request.headers.get("via", "")
    proto = request.headers.get("x-forwarded-proto", "")
    trace = request.headers.get("x-cloud-trace-context")

    return (
        "google" in via.lower() and
        proto == "https" and
        trace is not None
    )
