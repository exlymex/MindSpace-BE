from typing import List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
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


@router.get("/search", response_model=Optional[UserOut])
async def search_user_by_email(
        email: str = Query(..., description="Email користувача для пошуку"),
        role: Optional[str] = Query(None, description="Роль користувача (student, psychologist)"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Пошук користувача за email та опціонально за роллю."""
    user = await UserService.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з email {email} не знайдено"
        )

    if role and user.role.value != role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з email {email} та роллю {role} не знайдено"
        )

    return user


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Отримати інформацію про користувача за ID."""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено"
        )
    return user


@router.put("/me", response_model=UserOut)
async def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Update current user information"""
    try:
        updated_user = await UserService.update_user(
            db=db,
            user_id=current_user.id,
            user_data=user_update
        )
        return updated_user
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при оновленні користувача: {str(e)}"
        )


@router.post("/me/avatar", response_model=UserOut)
async def update_avatar(
        avatar: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """Update current user avatar"""
    try:
        updated_user = await UserService.update_avatar(
            db=db,
            user_id=current_user.id,
            avatar=avatar
        )
        return updated_user
    except Exception as e:
        print(f"Error updating avatar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при оновленні аватара: {str(e)}"
        )
