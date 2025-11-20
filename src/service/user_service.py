from src.dao.user_dao import UserDAO
from src.model.db.user_orm import UserORM
from src.model.view.user_view import UserView


class UserService:

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def authenticate_user(
        self, google_id: str, email: str, name: str, picture_url: str
    ) -> UserView:
        """
        Authenticates user and update profile from Google token.

        NOTE: Currently treats every authenticated request as a new "session".
        TODO: When session management is implemented, this will only be called on session creation.
        TODO: Add `get_user()` method for read-only access during session
        """
        user = self.user_dao.find_by_google_id(google_id)

        if user:
            user = self.user_dao.update_profile_and_login(
                google_id, email, name, picture_url
            )
        else:
            user = self.user_dao.create(
                user=UserORM(
                    google_id=google_id, email=email, name=name, picture_url=picture_url
                )
            )

        return UserView.model_validate(user)
