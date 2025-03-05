from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.messages import MessageOut
from app.schemas.users import UserOut


class ChatBase(BaseModel):
    student_id: int
    psychologist_id: int


class ChatCreate(ChatBase):
    pass


class ChatParticipantInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatOut(ChatBase):
    id: int
    created_at: datetime
    last_message: Optional[MessageOut] = None
    participant_info: Optional[ChatParticipantInfo] = None

    class Config:
        from_attributes = True
