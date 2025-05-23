from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.session import Session, SessionStatus
from app.models.user import User, UserRole
from app.schemas.sessions import SessionCreate, SessionUpdate


class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, session_data: SessionCreate, student_id: int) -> dict:
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
        
        query = select(User).where(User.id == session_data.psychologist_id)
        result = await db.execute(query)
        psychologist = result.scalars().first()
        
        return {
            "id": session.id,
            "student_id": session.student_id,
            "psychologist_id": session.psychologist_id,
            "date": session.date,
            "time": session.time,
            "duration": session.duration,
            "status": session.status,
            "notes": session.notes,
            "price": session.price,
            "psychologist_name": f"{psychologist.first_name} {psychologist.last_name}" if psychologist else "Невідомий психолог",
            "psychologist_avatar": psychologist.avatar_url if psychologist else None
        }

    @staticmethod
    async def get_session_by_id(db: AsyncSession, session_id: int, user_id: int) -> Optional[dict]:
        """
        Retrieves a session by its ID for a specific user.
        """
        query = (
            select(
                Session,
                User.first_name,
                User.last_name,
                User.avatar_url
            )
            .join(User, Session.psychologist_id == User.id)
            .where(
                Session.id == session_id,
                ((Session.student_id == user_id) | (Session.psychologist_id == user_id))
            )
        )
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        session = row[0]
        
        return {
            "id": session.id,
            "student_id": session.student_id,
            "psychologist_id": session.psychologist_id,
            "date": session.date,
            "time": session.time,
            "duration": session.duration,
            "status": session.status,
            "notes": session.notes,
            "price": session.price,
            "psychologist_name": f"{row.first_name} {row.last_name}" if row.first_name and row.last_name else "Невідомий психолог",
            "psychologist_avatar": row.avatar_url
        }

    @staticmethod
    async def get_user_sessions(db: AsyncSession, user_id: int) -> List[dict]:
        """
        Returns all sessions where the user is either the student or the psychologist,
        including psychologist name and avatar.
        """
        query = (
            select(
                Session,
                User.first_name,
                User.last_name,
                User.avatar_url
            )
            .join(User, Session.psychologist_id == User.id)
            .where((Session.student_id == user_id) | (Session.psychologist_id == user_id))
            .order_by(Session.date, Session.time)
        )
        
        result = await db.execute(query)
        
        session_dicts = []
        for row in result:
            session = row[0]
            
            session_dict = {
                "id": session.id,
                "student_id": session.student_id,
                "psychologist_id": session.psychologist_id,
                "date": session.date,
                "time": session.time,
                "duration": session.duration,
                "status": session.status,
                "notes": session.notes,
                "price": session.price,
                "psychologist_name": f"{row.first_name} {row.last_name}" if row.first_name and row.last_name else "Невідомий психолог",
                "psychologist_avatar": row.avatar_url
            }
            session_dicts.append(session_dict)
        
        return session_dicts

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
    async def update_session(db: AsyncSession, session_id: int, session_data: SessionUpdate) -> Optional[dict]:
        """
        Updates a session with new data.
        """
        query = select(Session).where(Session.id == session_id)
        result = await db.execute(query)
        session = result.scalars().first()
        
        if not session:
            return None

        try:
            update_data = session_data.model_dump(exclude_unset=True)
        except AttributeError:
            update_data = session_data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(session, key, value)

        await db.commit()
        await db.refresh(session)
        
        psych_query = select(User).where(User.id == session.psychologist_id)
        psych_result = await db.execute(psych_query)
        psychologist = psych_result.scalars().first()
        
        return {
            "id": session.id,
            "student_id": session.student_id,
            "psychologist_id": session.psychologist_id,
            "date": session.date,
            "time": session.time,
            "duration": session.duration,
            "status": session.status,
            "notes": session.notes,
            "price": session.price,
            "psychologist_name": f"{psychologist.first_name} {psychologist.last_name}" if psychologist else "Невідомий психолог",
            "psychologist_avatar": psychologist.avatar_url if psychologist else None
        }

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
