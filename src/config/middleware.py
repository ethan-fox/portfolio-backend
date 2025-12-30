from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings, Environment


def apply_middleware(app: FastAPI, settings: Settings) -> None:
    """Apply all middleware to the FastAPI application."""
    _apply_cors_middleware(app, settings)


def _apply_cors_middleware(app: FastAPI, settings: Settings) -> None:
    """Configure CORS based on environment.

    NOTE: Origins are hardcoded (not env-configurable) to prevent attackers
    from overriding CORS_ORIGINS env var and bypassing security.
    TODO: Consider making this environment-aware if we add a secure config system.
    """
    if settings.environment == Environment.LOCAL:
        allowed_origins = ["http://localhost:5173", "http://192.168.1.154:5173"]
    else:
        allowed_origins = ["https://ethan-builds.com"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
