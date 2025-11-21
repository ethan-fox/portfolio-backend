from fastapi import APIRouter, Depends, HTTPException, status

from src.config.dependency import get_content_service
from src.model.view.content_view import ContentView
from src.service.content_service import ContentService

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/resume", response_model=ContentView)
async def get_resume(service: ContentService = Depends(get_content_service)):
    result = service.get_resume()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume content not found"
        )

    return result
