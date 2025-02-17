import enum

from sqlalchemy import Column, Integer, String, Enum

from app.db.base import Base


class UserRole(enum.Enum):
    student = "student"
    psychologist = "psychologist"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    username = Column(String(50), unique=True, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)  # Додаємо роль
