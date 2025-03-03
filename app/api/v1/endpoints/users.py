from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.sessions import get_db
from app.models.user import User
from app.schemas.users import UserOut
from app.services.user_service import AuthService

router = APIRouter(tags=["users"])


@router.get("/psychologists", response_model=List[UserOut])
async def get_psychologists(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all psychologists"""
    return await AuthService.get_psychologists(db)
