CREATE TABLE IF NOT EXISTS signals (
    signal_id         UUID PRIMARY KEY,
    market_id         TEXT        NOT NULL,
    question          TEXT,
    direction         TEXT,
    market_price      NUMERIC,
    estimated_prob    NUMERIC,
    edge              NUMERIC,
    confidence        NUMERIC,
    kelly_fraction    NUMERIC,
    position_size     NUMERIC,
    spread            NUMERIC,
    liquidity         NUMERIC,
    volatility_regime TEXT,
    model_name        TEXT,
    slug              TEXT,
    status            TEXT,
    generated_at      TIMESTAMPTZ,
    resolved_at       TIMESTAMPTZ,
    realized_pnl      NUMERIC,
    order_id          TEXT,
    notes             TEXT,
    ingested_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_status      ON signals (status);
CREATE INDEX IF NOT EXISTS idx_signals_market      ON signals (market_id);
CREATE INDEX IF NOT EXISTS idx_signals_generated   ON signals (generated_at DESC);

CREATE TABLE IF NOT EXISTS positions (
    position_id              UUID PRIMARY KEY,
    signal_id                UUID REFERENCES signals (signal_id),
    market_id                TEXT        NOT NULL,
    question                 TEXT,
    city_code                TEXT,
    direction                TEXT,
    entry_price              NUMERIC,
    entry_temp_estimate_c    NUMERIC,
    size_usd                 NUMERIC,
    slug                     TEXT,
    order_id                 TEXT,
    token_id                 TEXT,
    temp_shift_threshold_c   NUMERIC,
    stop_loss_pct            NUMERIC,
    take_profit_pct          NUMERIC,
    status                   TEXT,
    opened_at                TIMESTAMPTZ,
    closed_at                TIMESTAMPTZ,
    exit_price               NUMERIC,
    exit_reason              TEXT,
    realized_pnl             NUMERIC,
    ingested_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_positions_status   ON positions (status);
CREATE INDEX IF NOT EXISTS idx_positions_market   ON positions (market_id);
CREATE INDEX IF NOT EXISTS idx_positions_opened   ON positions (opened_at DESC);
