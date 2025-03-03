import enum

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Float, Enum, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class SessionStatus(enum.Enum):
    upcoming = "upcoming"
    completed = "completed"
    cancelled = "cancelled"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(10), nullable=False)
    duration = Column(Integer, nullable=False)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.upcoming)
    notes = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="sessions")
    psychologist = relationship("User", foreign_keys=[psychologist_id], back_populates="psychologist_sessions")
