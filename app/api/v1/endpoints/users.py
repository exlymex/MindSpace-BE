from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.sessions import get_db
from app.models.user import User
from app.schemas.users import UserOut, UserUpdate
from app.services.user_service import AuthService, UserService

router = APIRouter(tags=["users"])


@router.get("/psychologists", response_model=List[UserOut])
async def get_psychologists(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all psychologists"""
    return await AuthService.get_psychologists(db)


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Отримати інформацію про поточного користувача."""
    return current_user


@router.put("/me", response_model=UserOut)
async def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Оновити інформацію про поточного користувача."""
    try:
        updated_user = await UserService.update_user(
            db=db,
            user_id=current_user.id,
            user_data=user_update
        )
        return updated_user
    except Exception as e:
        # Логуємо помилку для відлагодження
        print(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при оновленні користувача: {str(e)}"
        )
