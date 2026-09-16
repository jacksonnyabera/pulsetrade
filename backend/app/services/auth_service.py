import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.security_event import SecurityEvent
from app.models.session import Session
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str, full_name: str | None) -> User:
    user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


async def log_security_event(
    db: AsyncSession,
    user_id: uuid.UUID,
    event_type: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    event = SecurityEvent(user_id=user_id, event_type=event_type, ip_address=ip_address, user_agent=user_agent)
    db.add(event)
    await db.commit()


async def create_session(db: AsyncSession, user_id: uuid.UUID, jti: str, request: Request) -> Session:
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    session = Session(
        user_id=user_id,
        refresh_token_jti=jti,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )
    db.add(session)
    await db.commit()
    return session


async def revoke_session_by_jti(db: AsyncSession, jti: str) -> None:
    result = await db.execute(select(Session).where(Session.refresh_token_jti == jti))
    session = result.scalar_one_or_none()
    if session:
        session.is_revoked = True
        await db.commit()