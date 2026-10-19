from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    contract_id: int
    symbol: str = Field(min_length=2, max_length=30)
    contract_type: Literal["CALL", "PUT"]
    stake: float = Field(gt=0)
    currency: str = Field(min_length=2, max_length=10)
    duration: int = Field(gt=0)
    duration_unit: Literal["t", "s", "m"]


class TradeSettle(BaseModel):
    profit: float


class TradeOut(BaseModel):
    contract_id: int
    symbol: str
    contract_type: str
    stake: float
    currency: str
    duration: int
    duration_unit: str
    account_type: str
    status: str
    profit: float | None
    opened_at: datetime
    closed_at: datetime | None