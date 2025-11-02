from fastapi import FastAPI

from src.config.settings import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Application factory pattern."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version
    )

    # Register routers here

    @app.get("/")
    async def hello_world():
        """Hello World endpoint."""
        return {"message": "Hello World"}

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
