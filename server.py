import logging
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

# Absolute paths are safer for Windows
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CryptoTerminal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from storage.database import Database
DB_PATH = os.path.join(BASE_DIR, "data", "crypto_terminal.db")
db = Database(DB_PATH)

@app.get("/")
async def read_index():
    if not os.path.exists(INDEX_PATH):
        logger.error(f"Index file missing at {INDEX_PATH}")
        return JSONResponse(status_code=404, content={"detail": f"index.html not found at {INDEX_PATH}"})
    return FileResponse(INDEX_PATH)

@app.get("/api/health")
async def health():
    return {"status": "ok", "engine": "Cryptex", "path": INDEX_PATH}

@app.get("/api/prices/{symbol}")
async def get_prices(symbol: str, hours: int = 24):
    data = db.get_price_data(symbol, hours=hours)
    if not data: return generate_mock_ohlcv(symbol)
    formatted = []
    for d in data:
        ts = d['timestamp']
        if isinstance(ts, str):
            try: dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except: dt = datetime.utcnow()
        else: dt = ts
        formatted.append({"time": int(dt.timestamp()), "open": d['open'], "high": d['high'], "low": d['low'], "close": d['close']})
    return formatted

@app.get("/api/sentiment")
async def get_sentiment_overview():
    symbols = ["BTC", "ETH", "SOL", "ADA", "AVAX", "DOT", "MATIC", "LINK"]
    results = []
    for sym in symbols:
        sent = db.get_recent_sentiment(sym, hours=24)
        score = sent.get("avg_score", 0.5)
        results.append({"symbol": sym, "score": round(score * 100), "count": sent.get("count", 0), "label": "BULLISH" if score > 0.6 else "BEARISH" if score < 0.4 else "NEUTRAL"})
    return results

@app.get("/api/signals")
async def get_signals(limit: int = 10):
    import sqlalchemy
    query = sqlalchemy.text("SELECT * FROM trading_signals ORDER BY created_at DESC LIMIT :limit")
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(query, {"limit": limit})
            return [dict(row._mapping) for row in rows]
    except: return []

def generate_mock_ohlcv(symbol: str):
    base_price = {"BTC": 65000, "ETH": 3500, "SOL": 140}.get(symbol, 100)
    data = []
    now = datetime.utcnow()
    current_price = base_price
    for i in range(100):
        timestamp = now - timedelta(minutes=15 * (100 - i))
        change = random.uniform(-0.005, 0.005) * current_price
        open_p = current_price
        close_p = open_p + change
        data.append({"time": int(timestamp.timestamp()), "open": round(open_p, 2), "high": round(max(open_p, close_p) + 5, 2), "low": round(min(open_p, close_p) - 5, 2), "close": round(close_p, 2)})
        current_price = close_p
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
