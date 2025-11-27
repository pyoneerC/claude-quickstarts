"""
CRUD operations for database models.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import SessionDB, MessageDB


# ===== Session CRUD =====

async def create_session(
    db: AsyncSession,
    model: str,
    provider: str,
    system_prompt_suffix: Optional[str] = None
) -> SessionDB:
    """Create a new session."""
    session = SessionDB(
        id=str(uuid.uuid4()),
        model=model,
        provider=provider,
        system_prompt_suffix=system_prompt_suffix,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: str) -> Optional[SessionDB]:
    """Get a session by ID."""
    result = await db.execute(
        select(SessionDB).where(SessionDB.id == session_id)
    )
    return result.scalar_one_or_none()


async def get_sessions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[SessionDB]:
    """Get all sessions."""
    result = await db.execute(
        select(SessionDB)
        .order_by(SessionDB.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete_session(db: AsyncSession, session_id: str) -> bool:
    """Delete a session."""
    result = await db.execute(
        delete(SessionDB).where(SessionDB.id == session_id)
    )
    await db.commit()
    return result.rowcount > 0


async def update_session(
    db: AsyncSession,
    session_id: str,
    **kwargs
) -> Optional[SessionDB]:
    """Update a session."""
    session = await get_session(db, session_id)
    if not session:
        return None
    
    for key, value in kwargs.items():
        setattr(session, key, value)
    
    session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)
    return session


# ===== Message CRUD =====

async def create_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: list
) -> MessageDB:
    """Create a new message."""
    message = MessageDB(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages(
    db: AsyncSession,
    session_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[MessageDB]:
    """Get messages for a session."""
    result = await db.execute(
        select(MessageDB)
        .where(MessageDB.session_id == session_id)
        .order_by(MessageDB.timestamp.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_message(db: AsyncSession, message_id: str) -> Optional[MessageDB]:
    """Get a message by ID."""
    result = await db.execute(
        select(MessageDB).where(MessageDB.id == message_id)
    )
    return result.scalar_one_or_none()


async def delete_message(db: AsyncSession, message_id: str) -> bool:
    """Delete a message."""
    result = await db.execute(
        delete(MessageDB).where(MessageDB.id == message_id)
    )
    await db.commit()
    return result.rowcount > 0
