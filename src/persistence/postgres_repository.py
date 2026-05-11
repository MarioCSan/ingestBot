from __future__ import annotations

import logging
import os
from pathlib import Path

import asyncpg

from ..models import SignalMessage, PositionMessage

logger = logging.getLogger(__name__)

_SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text()


class PostgresRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def initialize(self) -> None:
        self._pool = await asyncpg.create_pool(self._dsn, min_size=2, max_size=10)
        async with self._pool.acquire() as conn:
            await conn.execute(_SCHEMA_SQL)
        logger.info("PostgreSQL pool ready — schema applied")

    async def upsert_signal(self, signal: SignalMessage) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO signals (
                    signal_id, market_id, question, direction, market_price,
                    estimated_prob, edge, confidence, kelly_fraction, position_size,
                    spread, liquidity, volatility_regime, model_name, slug, status,
                    generated_at, resolved_at, realized_pnl, order_id, notes
                ) VALUES (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
                    $11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21
                )
                ON CONFLICT (signal_id) DO UPDATE SET
                    status        = EXCLUDED.status,
                    resolved_at   = EXCLUDED.resolved_at,
                    realized_pnl  = EXCLUDED.realized_pnl,
                    order_id      = EXCLUDED.order_id,
                    notes         = EXCLUDED.notes
                """,
                signal.signal_id,
                signal.market_id,
                signal.question,
                signal.direction,
                signal.market_price,
                signal.estimated_probability,
                signal.edge,
                signal.confidence,
                signal.kelly_fraction,
                signal.position_size_usd,
                signal.spread,
                signal.liquidity,
                signal.volatility_regime,
                signal.model_name,
                signal.slug,
                signal.status,
                signal.generated_at,
                signal.resolved_at,
                signal.realized_pnl,
                signal.order_id,
                signal.notes,
            )

    async def upsert_position(self, position: PositionMessage) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO positions (
                    position_id, signal_id, market_id, question, city_code,
                    direction, entry_price, entry_temp_estimate_c, size_usd,
                    slug, order_id, token_id, temp_shift_threshold_c,
                    stop_loss_pct, take_profit_pct, status, opened_at,
                    closed_at, exit_price, exit_reason, realized_pnl
                ) VALUES (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
                    $11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21
                )
                ON CONFLICT (position_id) DO UPDATE SET
                    status       = EXCLUDED.status,
                    closed_at    = EXCLUDED.closed_at,
                    exit_price   = EXCLUDED.exit_price,
                    exit_reason  = EXCLUDED.exit_reason,
                    realized_pnl = EXCLUDED.realized_pnl
                """,
                position.position_id,
                position.signal_id,
                position.market_id,
                position.question,
                position.city_code,
                position.direction,
                position.entry_price,
                position.entry_temp_estimate_c,
                position.size_usd,
                position.slug,
                position.order_id,
                position.token_id,
                position.temp_shift_threshold_c,
                position.stop_loss_pct,
                position.take_profit_pct,
                position.status,
                position.opened_at,
                position.closed_at,
                position.exit_price,
                position.exit_reason,
                position.realized_pnl,
            )

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
