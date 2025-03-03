import enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, Date, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(enum.Enum):
    student = "student"
    psychologist = "psychologist"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)  # Додаємо роль
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)
    birth_date = Column(Date, nullable=True)
    phone_number = Column(String(20), nullable=True)

    # Зв'язки
    sessions = relationship("Session", back_populates="student", foreign_keys="Session.student_id")
    psychologist_sessions = relationship("Session", back_populates="psychologist",
                                         foreign_keys="Session.psychologist_id")
    materials = relationship("Material", back_populates="author")
