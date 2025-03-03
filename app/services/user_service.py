from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.users import UserCreate, UserLogin, UserUpdate


class AuthService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Creates a new user, hashes the password before saving."""
        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role=user_data.role
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: UserLogin):
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalars().first()

        if not user or not verify_password(login_data.password, user.hashed_password):
            return None

        access_token = create_access_token({"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def get_psychologists(db: AsyncSession):
        """Get all psychologists"""
        query = select(User).where(User.role == "psychologist")
        result = await db.execute(query)
        return result.scalars().all()


class UserService:
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Updates a user with new data.
        """
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()
        
        if not user:
            return None
        
        # Для Pydantic v2 використовуємо model_dump замість dict
        try:
            # Спочатку спробуємо новий метод для Pydantic v2
            update_data = user_data.model_dump(exclude_unset=True)
        except AttributeError:
            # Якщо не спрацювало, використовуємо старий метод для Pydantic v1
            update_data = user_data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user
