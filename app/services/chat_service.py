from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User
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
    async def list_chats_for_user(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
        """
        Returns all chats where the user is either the student or the psychologist,
        along with the last message for each chat and information about the other participant.
        """
        # Отримуємо всі чати користувача
        result = await db.execute(
            select(Chat).where(
                (Chat.student_id == user_id) | (Chat.psychologist_id == user_id)
            ).order_by(Chat.created_at)
        )
        chats = result.scalars().all()
        
        # Для кожного чату отримуємо останнє повідомлення та інформацію про співрозмовника
        chat_dicts = []
        for chat in chats:
            chat_dict = {
                "id": chat.id,
                "student_id": chat.student_id,
                "psychologist_id": chat.psychologist_id,
                "created_at": chat.created_at,
                "last_message": None,
                "participant_info": None
            }
            
            # Отримуємо останнє повідомлення для чату
            last_message = await ChatService.get_last_message(db, chat.id)
            if last_message:
                chat_dict["last_message"] = {
                    "id": last_message.id,
                    "chat_id": last_message.chat_id,
                    "sender_id": last_message.sender_id,
                    "text": last_message.text,
                    "created_at": last_message.created_at
                }
            
            # Визначаємо ID співрозмовника
            participant_id = chat.student_id if user_id == chat.psychologist_id else chat.psychologist_id
            
            # Отримуємо інформацію про співрозмовника
            participant = await ChatService.get_user_by_id(db, participant_id)
            if participant:
                chat_dict["participant_info"] = {
                    "id": participant.id,
                    "first_name": participant.first_name,
                    "last_name": participant.last_name,
                    "avatar_url": participant.avatar_url
                }
            
            chat_dicts.append(chat_dict)
            
        return chat_dicts

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
    async def get_last_message(db: AsyncSession, chat_id: int) -> Optional[Message]:
        """
        Returns the last message for a given chat.
        """
        result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Returns user by ID.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

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
