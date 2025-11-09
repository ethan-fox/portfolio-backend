from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint for liveness probes.

    Returns:
        dict: Simple status response indicating the service is alive
    """
    return {"status": "healthy"}
