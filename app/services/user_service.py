from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import UploadFile, HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole
from app.schemas.users import UserCreate, UserLogin, UserUpdate


class AuthService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Creates a new user, hashes the password before saving."""
        hashed_password = hash_password(user_data.password)

        # Створюємо базові поля користувача
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            birth_date=user_data.birth_date
        )

        # Додаємо поля для психологів, якщо роль - психолог
        if user_data.role == UserRole.psychologist:
            user.education = user_data.education
            user.specialization = user_data.specialization
            user.license_number = user_data.license_number
            user.experience_years = user_data.experience_years

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

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    async def get_psychologists(db: AsyncSession):
        """Get all psychologists"""
        query = select(User).where(User.role == UserRole.psychologist)
        result = await db.execute(query)
        return result.scalars().all()


class UserService:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Отримати користувача за ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Отримати користувача за email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
        """Оновити дані користувача."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError(f"Користувача з ID {user_id} не знайдено")

        # Оновлюємо базові поля користувача
        for field, value in user_data.dict(exclude_unset=True).items():
            # Перевіряємо, чи поле існує в моделі користувача
            if hasattr(user, field):
                setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_avatar(db: AsyncSession, user_id: int, avatar: UploadFile) -> User:
        """Оновити аватар користувача."""
        import os
        import uuid
        import aiofiles
        
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError(f"Користувача з ID {user_id} не знайдено")
        
        # Перевіряємо тип файлу
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if avatar.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дозволені лише файли формату JPEG, JPG або PNG"
            )
        
        # Створюємо директорію для зберігання аватарів, якщо вона не існує
        upload_dir = os.path.join("static", "avatars")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Генеруємо унікальне ім'я файлу
        file_extension = avatar.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Зберігаємо файл
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await avatar.read()
            await out_file.write(content)
        
        # Оновлюємо URL аватара в базі даних
        # Використовуємо відносний шлях для зберігання в БД
        avatar_url = f"/static/avatars/{unique_filename}"
        user.avatar_url = avatar_url
        
        await db.commit()
        await db.refresh(user)
        return user
