from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.student
    first_name: str
    last_name: str
    phone_number: str
    birth_date: date
    # Додаткові поля для психологів
    education: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[float] = None

    @validator('birth_date')
    def validate_birth_date(cls, v):
        # Якщо передано datetime, конвертуємо в date
        if hasattr(v, 'date'):
            return v.date()
        return v

    @validator('education', 'specialization', 'license_number', 'experience_years')
    def validate_psychologist_fields(cls, v, values):
        if 'role' in values and values['role'] == UserRole.psychologist:
            if v is None:
                raise ValueError('Це поле обов\'язкове для психологів')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для оновлення даних користувача."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    # Додаткові поля для психологів
    education: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "first_name": "Іван",
                "last_name": "Петренко",
                "bio": "Короткий опис про себе",
                "phone_number": "+380501234567",
                "birth_date": "1990-01-01",
                "education": "Київський національний університет",
                "specialization": "Клінічна психологія",
                "license_number": "PSY12345",
                "experience_years": 5
            }
        }


class UserOut(UserBase):
    id: int
    role: UserRole
    first_name: str
    last_name: str
    phone_number: str
    birth_date: date
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    education: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[float] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
