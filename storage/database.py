import logging
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text, MetaData, Table, insert, select, desc, func
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        """
        Initializes the database, creates tables if they don't exist.
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Use StaticPool for SQLite to handle multiple threads in Streamlit/Pipelines
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.metadata = MetaData()
        self._init_db()

    def _init_db(self):
        """Runs the schema.sql file to initialize tables."""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        try:
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            
            with self.engine.connect() as conn:
                # SQLite executescript style
                raw_conn = conn.connection
                cursor = raw_conn.cursor()
                cursor.executescript(schema_sql)
                raw_conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    def insert_price_data(self, records: List[Dict[str, Any]]):
        """
        Bulk insert OHLCV records.
        Args:
            records: List of dictionaries with OHLCV data.
        """
        if not records:
            return
        
        query = text("""
            INSERT OR REPLACE INTO price_data (symbol, timestamp, open, high, low, close, volume)
            VALUES (:symbol, :timestamp, :open, :high, :low, :close, :volume)
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(query, records)
                conn.commit()
            logger.debug(f"Inserted {len(records)} price records.")
        except Exception as e:
            logger.error(f"Error inserting price data: {e}")

    def get_price_data(self, symbol: str, hours: int = 168) -> List[Dict[str, Any]]:
        """
        Get last N hours of candles for a symbol.
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT * FROM price_data 
            WHERE symbol = :symbol AND timestamp >= :since
            ORDER BY timestamp ASC
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"symbol": symbol, "since": since})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            return []

    def insert_sentiment(self, record: Dict[str, Any]):
        """Saves a sentiment record."""
        query = text("""
            INSERT INTO sentiment_records (source, symbol, text_snippet, sentiment_label, sentiment_score, raw_text)
            VALUES (:source, :symbol, :text_snippet, :sentiment_label, :sentiment_score, :raw_text)
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(query, record)
                conn.commit()
        except Exception as e:
            logger.error(f"Error inserting sentiment: {e}")

    def get_recent_sentiment(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Aggregates sentiment scores for a symbol."""
        since = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT AVG(sentiment_score) as avg_score, COUNT(*) as count
            FROM sentiment_records
            WHERE symbol = :symbol AND created_at >= :since
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"symbol": symbol, "since": since}).fetchone()
                if result:
                    return {"avg_score": result[0] or 0.5, "count": result[1]}
                return {"avg_score": 0.5, "count": 0}
        except Exception as e:
            logger.error(f"Error fetching recent sentiment: {e}")
            return {"avg_score": 0.5, "count": 0}

    def insert_signal(self, signal: Dict[str, Any]):
        """Saves a trading signal."""
        query = text("""
            INSERT INTO trading_signals (symbol, signal_type, confidence, sentiment_score, price_prediction, onchain_signal, reasoning)
            VALUES (:symbol, :signal_type, :confidence, :sentiment_score, :price_prediction, :onchain_signal, :reasoning)
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(query, signal)
                conn.commit()
        except Exception as e:
            logger.error(f"Error inserting signal: {e}")

    def get_signals(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent signals for a symbol."""
        query = text("""
            SELECT * FROM trading_signals
            WHERE symbol = :symbol
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"symbol": symbol, "limit": limit})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error fetching signals: {e}")
            return []

    def insert_whale_tx(self, tx: Dict[str, Any]):
        """Saves a whale transaction."""
        query = text("""
            INSERT OR IGNORE INTO whale_transactions (tx_hash, symbol, from_address, to_address, value_usd, direction, timestamp)
            VALUES (:tx_hash, :symbol, :from_address, :to_address, :value_usd, :direction, :timestamp)
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(query, tx)
                conn.commit()
        except Exception as e:
            logger.error(f"Error inserting whale tx: {e}")

    def get_whale_txs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch recent whale movements."""
        since = datetime.utcnow() - timedelta(hours=hours)
        query = text("""
            SELECT * FROM whale_transactions
            WHERE timestamp >= :since
            ORDER BY timestamp DESC
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"since": since})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error fetching whale txs: {e}")
            return []

    def save_backtest(self, result: Dict[str, Any]):
        """Saves backtest results."""
        query = text("""
            INSERT INTO backtest_results (symbol, start_date, end_date, total_trades, winning_trades, win_rate, total_pnl_pct, sharpe_ratio, max_drawdown)
            VALUES (:symbol, :start_date, :end_date, :total_trades, :winning_trades, :win_rate, :total_pnl_pct, :sharpe_ratio, :max_drawdown)
        """)
        try:
            with self.engine.connect() as conn:
                conn.execute(query, result)
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving backtest: {e}")
