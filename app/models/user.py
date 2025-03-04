import enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, Date, Enum, Float
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
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Базові поля для всіх користувачів
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)
    birth_date = Column(Date, nullable=False)
    phone_number = Column(String(20), nullable=False)

    # Поля для психологів
    education = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    experience_years = Column(Float, nullable=True)

    # Зв'язки
    sessions = relationship("Session", back_populates="student", foreign_keys="Session.student_id")
    psychologist_sessions = relationship("Session", back_populates="psychologist",
                                         foreign_keys="Session.psychologist_id")
    materials = relationship("Material", back_populates="author")
