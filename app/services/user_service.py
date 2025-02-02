from sqlalchemy.orm import Session
from app.models.user import User            # Import User directly from models/users.py
from app.schemas.users import UserCreate      # Import UserCreate directly from schemas/users.py
from app.core.security import get_password_hash

def create_user(db: Session, user_in: UserCreate):
    # Hash the password before saving
    hashed_password = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
