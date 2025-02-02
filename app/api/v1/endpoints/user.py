from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app import db
from app.services import user_service
from app.schemas.users import UserOut, UserCreate  # Import directly
from app.db.sessions import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists, create new user, etc.
    user = user_service.create_user(db, user_in)
    return user
