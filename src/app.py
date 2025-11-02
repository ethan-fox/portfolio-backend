from fastapi import FastAPI

from src.config.settings import get_settings
from src.router import subscriber_router

settings = get_settings()


def create_app() -> FastAPI:
    """Application factory pattern."""
    app = FastAPI(title=settings.api_title, version=settings.api_version)

    app.include_router(subscriber_router.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app", host="0.0.0.0", port=7050, reload=settings.environment == "LOCAL"
    )
