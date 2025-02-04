from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.users import UserCreate


class AuthService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Creates a new user, hashes the password before saving."""
        hashed_password = hash_password(user_data.password)
        user = User(email=user_data.email, hashed_password=hashed_password, username=user_data.username)

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
