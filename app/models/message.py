from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)  # or String(1000) with a length
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    chat = relationship("Chat", back_populates="messages")
