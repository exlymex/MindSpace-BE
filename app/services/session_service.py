from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.session import Session, SessionStatus
from app.models.user import User, UserRole
from app.schemas.sessions import SessionCreate, SessionUpdate


class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, session_data: SessionCreate, student_id: int) -> Session:
        """
        Creates a new session booking.
        """
        session = Session(
            student_id=student_id,
            psychologist_id=session_data.psychologist_id,
            date=session_data.date,
            time=session_data.time,
            duration=session_data.duration,
            price=session_data.price,
            status="upcoming"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: int, user_id: int) -> Optional[Session]:
        """
        Retrieves a session by its ID for a specific user.
        """
        query = select(Session).where(
            Session.id == session_id,
            ((Session.student_id == user_id) | (Session.psychologist_id == user_id))
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_user_sessions(db: AsyncSession, user_id: int) -> List[Session]:
        """
        Returns all sessions where the user is either the student or the psychologist.
        """
        query = select(Session).where(
            (Session.student_id == user_id) | (Session.psychologist_id == user_id)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_psychologist_by_id(db: AsyncSession, psychologist_id: int) -> Optional[User]:
        """
        Retrieves a psychologist by their ID.
        """
        query = select(User).where(
            User.id == psychologist_id,
            User.role == UserRole.psychologist
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def update_session(db: AsyncSession, session_id: int, session_data: SessionUpdate) -> Optional[Session]:
        """
        Updates a session with new data.
        """
        session = await SessionService.get_session_by_id(db, session_id, session_data.student_id)
        if not session:
            return None

        # Для Pydantic v2 використовуємо model_dump замість dict
        try:
            # Спочатку спробуємо новий метод для Pydantic v2
            update_data = session_data.model_dump(exclude_unset=True)
        except AttributeError:
            # Якщо не спрацювало, використовуємо старий метод для Pydantic v1
            update_data = session_data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(session, key, value)

        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def cancel_session(db: AsyncSession, session_id: int) -> bool:
        """
        Cancels a session by setting its status to cancelled.
        """
        query = select(Session).where(Session.id == session_id)
        result = await db.execute(query)
        session = result.scalars().first()
        
        if session:
            session.status = "cancelled"
            await db.commit()
            return True
        return False
