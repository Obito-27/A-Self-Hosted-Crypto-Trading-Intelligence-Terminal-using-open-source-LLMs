-- Price Data Table
CREATE TABLE IF NOT EXISTS price_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    UNIQUE(symbol, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_price_symbol_time ON price_data(symbol, timestamp);

-- Sentiment Records Table
CREATE TABLE IF NOT EXISTS sentiment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL, -- reddit/news
    symbol TEXT NOT NULL,
    text_snippet TEXT NOT NULL,
    sentiment_label TEXT NOT NULL, -- BULLISH/BEARISH/NEUTRAL/FUD
    sentiment_score REAL NOT NULL, -- 0 to 1
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_text TEXT
);

CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON sentiment_records(symbol);

-- Trading Signals Table
CREATE TABLE IF NOT EXISTS trading_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL, -- BUY/SELL/HOLD
    confidence REAL NOT NULL, -- 0 to 1
    sentiment_score REAL,
    price_prediction TEXT,
    onchain_signal TEXT,
    reasoning TEXT, -- JSON format
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    outcome TEXT -- NULL until verified
);

-- Whale Transactions Table
CREATE TABLE IF NOT EXISTS whale_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    from_address TEXT,
    to_address TEXT,
    value_usd REAL,
    direction TEXT NOT NULL, -- EXCHANGE_INFLOW/EXCHANGE_OUTFLOW/WALLET_TO_WALLET
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Backtest Results Table
CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    total_trades INTEGER,
    winning_trades INTEGER,
    win_rate REAL,
    total_pnl_pct REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Source Accuracy Tracker Table
CREATE TABLE IF NOT EXISTS source_accuracy (
    source TEXT PRIMARY KEY, -- e.g., 'r/cryptocurrency', 'CoinDesk'
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    avg_error REAL DEFAULT 0,
    reliability_score REAL DEFAULT 0.5,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
