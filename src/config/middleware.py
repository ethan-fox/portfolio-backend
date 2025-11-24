import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings, Environment

logger = logging.getLogger(__name__)


def apply_middleware(app: FastAPI, settings: Settings) -> None:
    """Apply all middleware to the FastAPI application."""
    _apply_static_file_security_middleware(app)
    _apply_cors_middleware(app, settings)


def _apply_static_file_security_middleware(app: FastAPI) -> None:
    """Add security middleware to prevent path traversal attacks on static files."""

    @app.middleware("http")
    async def validate_static_paths(request: Request, call_next):
        if request.url.path.startswith("/img/"):
            suspicious_patterns = ["..", "~", "\\", "%2e%2e", "%2f%2f", "//"]

            for pattern in suspicious_patterns:
                if pattern in request.url.path.lower():
                    logger.warning(
                        f"Path traversal attempt blocked: path='{request.url.path}', "
                        f"client={request.client.host if request.client else 'unknown'}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied"
                    )

        return await call_next(request)


def _apply_cors_middleware(app: FastAPI, settings: Settings) -> None:
    """Configure CORS based on environment.

    NOTE: Origins are hardcoded (not env-configurable) to prevent attackers
    from overriding CORS_ORIGINS env var and bypassing security.
    TODO: Consider making this environment-aware if we add a secure config system.
    """
    if settings.environment == Environment.LOCAL:
        allowed_origins = ["http://localhost:5173"]
    else:
        allowed_origins = ["https://ethan-builds.com"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
