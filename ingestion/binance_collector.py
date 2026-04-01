import aiohttp
import asyncio
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from storage.database import Database

logger = logging.getLogger(__name__)

class BinanceCollector:
    BASE_URL = "https://api.binance.com"
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]
    SYMBOL_MAP = {
        "BTCUSDT": "BTC",
        "ETHUSDT": "ETH",
        "SOLUSDT": "SOL",
        "BNBUSDT": "BNB",
        "ADAUSDT": "ADA"
    }

    async def fetch_ohlcv(self, session: aiohttp.ClientSession, symbol: str, interval: str = "15m", limit: int = 200) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV candles from Binance public API.
        Args:
            session: aiohttp session
            symbol: Binance symbol (e.g., BTCUSDT)
            interval: Candle interval
            limit: Number of candles to fetch
        Returns:
            List of OHLCV dictionaries
        """
        url = f"{self.BASE_URL}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        display_symbol = self.SYMBOL_MAP.get(symbol, symbol)
        
        for attempt in range(3):
            try:
                async with session.get(url, params=params) as response:
                    logger.debug(f"Binance OHLCV {symbol} status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        records = []
                        for item in data:
                            # [openTime, open, high, low, close, volume, closeTime, ...]
                            records.append({
                                'symbol': display_symbol,
                                'timestamp': datetime.utcfromtimestamp(item[0] / 1000.0),
                                'open': float(item[1]),
                                'high': float(item[2]),
                                'low': float(item[3]),
                                'close': float(item[4]),
                                'volume': float(item[5])
                            })
                        return records
                    elif response.status == 429:
                        logger.warning(f"Binance rate limit hit. Waiting 60s...")
                        await asyncio.sleep(60)
                    else:
                        logger.warning(f"Binance error {response.status}: {await response.text()}")
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
            
            await asyncio.sleep(30)
        
        return []

    async def fetch_all_symbols(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch OHLCV for all SYMBOLS concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_ohlcv(session, symbol) for symbol in self.SYMBOLS]
            results = await asyncio.gather(*tasks)
            return dict(zip(self.SYMBOLS, results))

    async def get_current_price(self, symbol: str) -> float:
        """Get latest price from /api/v3/ticker/price endpoint."""
        url = f"{self.BASE_URL}/api/v3/ticker/price"
        params = {"symbol": symbol}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
        return 0.0

    async def run_once(self, db: Database):
        """Fetch and store data once."""
        all_data = await self.fetch_all_symbols()
        total_inserted = 0
        for symbol, records in all_data.items():
            if records:
                db.insert_price_data(records)
                total_inserted += len(records)
        logger.info(f"Binance collection cycle complete. Inserted {total_inserted} records.")

    async def run_continuous_async(self, db: Database, interval_seconds: int = 60):
        """Async loop for continuous fetching."""
        while True:
            await self.run_once(db)
            await asyncio.sleep(interval_seconds)

    def run_continuous(self, db: Database, interval_seconds: int = 60):
        """Entry point for running in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_continuous_async(db, interval_seconds))
