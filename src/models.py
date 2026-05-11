from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class SignalMessage(BaseModel):
    signal_id: UUID
    market_id: str
    question: Optional[str] = None
    direction: str
    market_price: float
    estimated_probability: float
    edge: float
    confidence: float
    kelly_fraction: float
    position_size_usd: float
    spread: float
    liquidity: float
    volatility_regime: Optional[str] = None
    model_name: Optional[str] = None
    slug: Optional[str] = ""
    status: str
    generated_at: datetime
    resolved_at: Optional[datetime] = None
    realized_pnl: Optional[float] = None
    order_id: Optional[str] = None
    notes: Optional[str] = ""

    @field_validator("generated_at", "resolved_at", mode="before")
    @classmethod
    def parse_dt(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class PositionMessage(BaseModel):
    position_id: UUID
    signal_id: UUID
    market_id: str
    question: Optional[str] = None
    city_code: Optional[str] = None
    direction: Optional[str] = None
    entry_price: float
    entry_temp_estimate_c: Optional[float] = None
    size_usd: float
    slug: Optional[str] = ""
    order_id: Optional[str] = ""
    token_id: Optional[str] = ""
    temp_shift_threshold_c: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    status: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    realized_pnl: Optional[float] = None

    @field_validator("opened_at", "closed_at", mode="before")
    @classmethod
    def parse_dt(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
