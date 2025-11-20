from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.sql import func
from src.model.db.user_orm import UserORM

class UserDAO:

    def __init__(self, db: Session):
        self.db = db

    def find_by_google_id(self, google_id: str) -> UserORM | None:
        return self.db.query(UserORM).filter(UserORM.google_id == google_id).first()

    def create(self, user: UserORM) -> UserORM:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_profile_and_login(self, google_id: str, email: str, name: str, picture_url: str) -> UserORM:
        # NOTE revisit this when dealing w session mgmt
        stmt = (
            update(UserORM)
            .where(UserORM.google_id == google_id)
            .values(
                email=email,
                name=name,
                picture_url=picture_url,
                last_login_at=func.current_timestamp()
            )
            .returning(UserORM)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one()