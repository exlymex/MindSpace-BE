from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    chat_id: int
    sender_id: int
    text: str


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
