import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (UniqueConstraint("user_id", "deriv_contract_id", name="uq_trades_user_contract"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    deriv_contract_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(10), nullable=False)
    stake: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    duration_unit: Mapped[str] = mapped_column(String(2), nullable=False)
    account_type: Mapped[str] = mapped_column(String(10), default="demo", nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="open", nullable=False)
    profit: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)