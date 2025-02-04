from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sessions import get_db
from app.models.user import User
from app.schemas.users import UserOut, UserCreate
from app.services.user_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """User registration with a check to see if the email is already taken."""
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exist")

    user = await AuthService.create_user(db, user_data)
    return user
