from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

from src.config.dependency import get_user_service
from src.config.settings import get_settings, Settings
from src.model.view.user_view import UserView
from src.service.user_service import UserService

security = HTTPBearer()


def verify_google_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict:
    """
    Verifies Google OAuth 2.0 ID token and returns token payload.

    Returns:
        dict: Token payload containing user info (sub, email, name, picture)

    Raises:
        HTTPException: If token is invalid or verification fails
    """
    token = credentials.credentials

    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), settings.google_oauth_client_id
        )

        if idinfo.get("iss") not in [
            "accounts.google.com",
            "https://accounts.google.com",
        ]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer"
            )

        return idinfo

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def get_current_user(
    token_payload: dict = Depends(verify_google_token),
    user_service: UserService = Depends(get_user_service),
) -> UserView:
    """
    Verifies Google token and authenticates user (creates if new, updates if existing).

    This is the primary authentication dependency for protected routes.
    Use as: current_user: UserView = Depends(get_current_user)

    Current behavior: Treats every authenticated request as a new "session"
    Future: When session management is implemented, this will validate session tokens
            and only call authenticate_user() on session creation.

    Returns:
        UserView: The authenticated user (view model, not ORM)
    """
    google_id = token_payload["sub"]
    email = token_payload["email"]
    name = token_payload.get("name", "")
    picture = token_payload.get("picture", "")

    return user_service.authenticate_user(google_id, email, name, picture)
