from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from src.config.dependency import get_guessr_service, get_content_service
from src.service.guessr_service import GuessrService
from src.service.content_service import ContentService
from src.model.view.guessr_list_view import GuessrListView
from src.model.view.guessr_item_view import GuessrItemView
from src.model.view.batch_guess_validation_view import BatchGuessValidationView
from src.model.view.content_view import ContentView
from src.model.api.batch_guess_request import BatchGuessRequest


router = APIRouter(prefix="/guessr", tags=["guessr"])


@router.get("/summary", response_model=list[GuessrItemView])
async def get_all_guessrs(service: GuessrService = Depends(get_guessr_service)):
    """
    Get all available guessrs ordered by date (newest first).
    Public endpoint - no authentication required.
    Returns a list of guessr entries with id and date.
    """
    return service.get_all_guessrs()


def _validate_date_range(puzzle_date: date) -> None:
    """
    Validate that the requested date is within the allowed range.
    - Cannot be in the future
    - Cannot be more than 7 days in the past
    """
    eastern = ZoneInfo("America/New_York")
    current_date_et = datetime.now(eastern).date()

    if puzzle_date > current_date_et:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot request puzzles for future dates. Current date (US Eastern): {current_date_et}"
        )

    oldest_allowed_date = current_date_et - timedelta(days=7)
    if puzzle_date < oldest_allowed_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot request puzzles older than 7 days. Oldest allowed date: {oldest_allowed_date}"
        )


@router.get("/", response_model=GuessrListView)
async def get_puzzles(
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    service: GuessrService = Depends(get_guessr_service)
):
    """
    Get guessr (3 puzzles) for a specific date.
    Public endpoint - no authentication required.
    Only allows dates within 7 days (past to present, US Eastern time).
    Returns guessr ID which can be used for POST validation.
    """
    _validate_date_range(date)
    return service.get_puzzles_for_date(date)


@router.post("/{guessr_id}", response_model=BatchGuessValidationView)
async def validate_guesses(
    guessr_id: int = Path(..., description="Guessr ID (from GET response)"),
    request: BatchGuessRequest = ...,
    service: GuessrService = Depends(get_guessr_service)
):
    """
    Validate multiple year guesses for a guessr.
    Public endpoint - no authentication required.
    Uses guessr ID to lookup the date and validate all puzzle guesses.
    Returns individual validation results with scores (0-33 per puzzle) and overall score (1-100 points total).
    """
    try:
        return service.validate_guesses(guessr_id, request.guesses)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/how-to-play", response_model=ContentView)
async def get_how_to_play(service: ContentService = Depends(get_content_service)):
    """
    Get how-to-play instructions in markdown format.
    Public endpoint - no authentication required.
    """
    result = service.get_how_to_play()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content could not be sourced."
        )

    return result
