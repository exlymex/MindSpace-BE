import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.sessions import get_db
from app.models.user import User
from app.schemas.sessions import SessionCreate, SessionOut, SessionUpdate
from app.services.session_service import SessionService

router = APIRouter(tags=["sessions"])

logger = logging.getLogger(__name__)


@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
        session_data: SessionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Creates a new session booking.
    """
    session_dict = await SessionService.create_session(db, session_data, current_user.id)
    return session_dict


@router.get("/", response_model=List[SessionOut])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all sessions for the current user"""
    return await SessionService.get_user_sessions(db, current_user.id)


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session by ID"""
    session = await SessionService.get_session_by_id(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.patch("/{session_id}", response_model=SessionOut)
async def update_session(
        session_id: int,
        session_data: SessionUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Updates a session with new data.
    """
    session = await SessionService.get_session_by_id(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["student_id"] != current_user.id and session["psychologist_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You are not a participant of this session")

    updated_session = await SessionService.update_session(db, session_id, session_data)
    if not updated_session:
        raise HTTPException(status_code=404, detail="Failed to update session")
    
    return updated_session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a session"""
    session = await SessionService.get_session_by_id(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    await SessionService.cancel_session(db, session_id)
    return {"detail": "Session cancelled successfully"}
