import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class DerivAccount(Base):
    __tablename__ = "deriv_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    deriv_loginid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "demo" or "real"
    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)