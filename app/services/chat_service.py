from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.chat import Chat
from app.models.message import Message
from app.schemas.chat import ChatCreate
from app.schemas.messages import MessageCreate


class ChatService:
    @staticmethod
    async def create_chat(db: AsyncSession, chat_data: ChatCreate) -> Chat:
        """
        Creates a new Chat (one student, one psychologist).
        """
        chat = Chat(**chat_data.dict())
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def get_chat_by_id(db: AsyncSession, chat_id: int) -> Optional[Chat]:
        """
        Retrieves a Chat by its ID.
        """
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalars().first()

    @staticmethod
    async def list_chats_for_user(db: AsyncSession, user_id: int) -> List[Chat]:
        """
        Returns all chats where the user is either the student or the psychologist.
        """
        result = await db.execute(
            select(Chat).where(
                (Chat.student_id == user_id) | (Chat.psychologist_id == user_id)
            ).order_by(Chat.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_chat_messages(db: AsyncSession, chat_id: int) -> List[Message]:
        """
        Returns all messages for a given chat, sorted by creation time.
        """
        result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def save_message(db: AsyncSession, msg_data: MessageCreate) -> Message:
        """
        Saves a new message in the given chat.
        """
        msg = Message(**msg_data.dict())
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg
