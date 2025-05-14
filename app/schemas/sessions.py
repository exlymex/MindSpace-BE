from typing import Optional

from pydantic import BaseModel

from app.models.session import SessionStatus


class SessionBase(BaseModel):
    psychologist_id: int
    date: str  # ISO формат дати
    time: str  # Час у форматі "HH:MM"
    duration: int  # Тривалість у хвилинах
    price: float


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    duration: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[SessionStatus] = None


class SessionOut(BaseModel):
    id: int
    student_id: int
    psychologist_id: int
    date: str
    time: str
    duration: int
    status: SessionStatus
    notes: Optional[str] = None
    price: Optional[float] = None
    psychologist_name: str
    psychologist_avatar: Optional[str] = None

    class Config:
        from_attributes = True
