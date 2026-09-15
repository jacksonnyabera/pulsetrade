from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
import uuid

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

from app.models.security_event import SecurityEvent


async def log_security_event(
    db: AsyncSession, user_id: uuid.UUID, event_type: str, ip_address: str | None = None, user_agent: str | None = None
) -> None:
    event = SecurityEvent(user_id=user_id, event_type=event_type, ip_address=ip_address, user_agent=user_agent)
    db.add(event)
    await db.commit()