from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.sessions import get_db
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatOut
from app.schemas.messages import MessageOut
from app.services.chat_service import ChatService

router = APIRouter(tags=["chats"])


@router.post("/", response_model=ChatOut)
async def create_chat(
        chat_data: ChatCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Creates a new chat with a given psychologist (or student).
    In practice, you might check the current_user role or ID.
    """
    # Optionally ensure current_user is actually a student or that
    # chat_data.student_id == current_user.id, etc.
    chat = await ChatService.create_chat(db, chat_data)
    return chat


@router.get("/", response_model=List[ChatOut])
async def list_user_chats(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Lists all chats where the current_user is either the student or the psychologist,
    along with the last message for each chat.
    """
    chats = await ChatService.list_chats_for_user(db, current_user.id)
    return chats


@router.get("/{chat_id}/messages", response_model=List[MessageOut])
async def get_chat_messages(
        chat_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieves all messages for a given chat.
    """
    chat = await ChatService.get_chat_by_id(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Ensure the user is part of this chat
    if chat.student_id != current_user.id and chat.psychologist_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not a participant of this chat")

    messages = await ChatService.get_chat_messages(db, chat_id)
    return messages
