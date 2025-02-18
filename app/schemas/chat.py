from datetime import datetime

from pydantic import BaseModel


class ChatBase(BaseModel):
    student_id: int
    psychologist_id: int


class ChatCreate(ChatBase):
    pass


class ChatOut(ChatBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
