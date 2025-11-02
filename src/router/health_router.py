from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Health check endpoint for liveness probes.

    Returns:
        dict: Simple status response indicating the service is alive
    """
    return {"status": "healthy"}
