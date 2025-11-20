from fastapi import APIRouter, Depends, status

from src.config.dependency import get_subscriber_service
from src.model.view.user_view import UserView
from src.service.subscriber_service import SubscriberService
from src.model.api.contact_request import ContactRequest
from src.model.view.contact_view import ContactView
from src.util.auth import get_current_user

router = APIRouter(prefix="/subscriber", tags=["subscriber"])


@router.post("/", response_model=ContactView, status_code=status.HTTP_201_CREATED)
async def create_subscriber(
    contact_data: ContactRequest,
    service: SubscriberService = Depends(get_subscriber_service),
    current_user: UserView = Depends(get_current_user)
):
    """Create a new subscriber."""
    return service.store_signup(contact_data)


@router.get("/", response_model=list[ContactView])
async def get_all_subscribers(
    service: SubscriberService = Depends(get_subscriber_service),
    current_user: UserView = Depends(get_current_user)
):
    """Get all subscribers."""
    return service.get_all_signups()
