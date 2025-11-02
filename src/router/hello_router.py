from fastapi import APIRouter


router = APIRouter(prefix="/hello", tags=["hello"])


@router.get("/")
async def hello_world():
    """Hello World endpoint."""
    return {"message": "Hello World"}
