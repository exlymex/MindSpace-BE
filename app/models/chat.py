from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships to the User table
    student = relationship("User", foreign_keys=[student_id])
    psychologist = relationship("User", foreign_keys=[psychologist_id])

    # optional: if you want to retrieve messages via relationship
    messages = relationship("Message", back_populates="chat")
