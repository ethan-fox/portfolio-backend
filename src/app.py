from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.config.settings import get_settings
from src.router import hello_router
from alembic.migration_runner import run_migrations

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Run database migrations
    run_migrations()
    yield
    # Shutdown: Clean up resources if needed


def create_app() -> FastAPI:
    """Application factory pattern."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        lifespan=lifespan
    )

    # Register routers
    app.include_router(hello_router.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "LOCAL"
    )
