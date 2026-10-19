from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.trade import Trade
from app.models.user import User
from app.schemas.trade import TradeCreate, TradeOut, TradeSettle

router = APIRouter(prefix="/trades", tags=["trades"])


def money(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))


def to_out(t: Trade) -> TradeOut:
    return TradeOut(
        contract_id=t.deriv_contract_id,
        symbol=t.symbol,
        contract_type=t.contract_type,
        stake=float(t.stake),
        currency=t.currency,
        duration=t.duration,
        duration_unit=t.duration_unit,
        account_type=t.account_type,
        status=t.status,
        profit=float(t.profit) if t.profit is not None else None,
        opened_at=t.opened_at,
        closed_at=t.closed_at,
    )


async def find_trade(db: AsyncSession, user_id: UUID, contract_id: int) -> Trade | None:
    result = await db.execute(select(Trade).where(Trade.user_id == user_id, Trade.deriv_contract_id == contract_id))
    return result.scalar_one_or_none()


@router.post("", response_model=TradeOut)
async def record_trade(
    payload: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await find_trade(db, current_user.id, payload.contract_id)
    if existing:
        return to_out(existing)
    trade = Trade(
        user_id=current_user.id,
        deriv_contract_id=payload.contract_id,
        symbol=payload.symbol,
        contract_type=payload.contract_type,
        stake=money(payload.stake),
        currency=payload.currency,
        duration=payload.duration,
        duration_unit=payload.duration_unit,
        account_type="demo",
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return to_out(trade)


@router.post("/{contract_id}/settle", response_model=TradeOut)
async def settle_trade(
    contract_id: int,
    payload: TradeSettle,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trade = await find_trade(db, current_user.id, contract_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.status != "open":
        return to_out(trade)
    trade.profit = money(payload.profit)
    trade.status = "won" if payload.profit > 0 else "lost" if payload.profit < 0 else "draw"
    trade.closed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(trade)
    return to_out(trade)


@router.get("", response_model=list[TradeOut])
async def list_trades(
    limit: int = Query(200, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade).where(Trade.user_id == current_user.id).order_by(Trade.opened_at.desc()).limit(limit)
    )
    return [to_out(t) for t in result.scalars().all()]