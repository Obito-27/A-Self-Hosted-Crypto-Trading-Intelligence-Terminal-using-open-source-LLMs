import logging
import threading
import time
from typing import Dict
from ingestion.binance_collector import BinanceCollector
from ingestion.reddit_collector import RedditCollector
from ingestion.news_collector import NewsCollector
from ingestion.onchain_collector import OnChainCollector
from storage.database import Database
from rich.console import Console
from rich.progress import Progress

logger = logging.getLogger(__name__)
console = Console()

class DataPipeline:
    def __init__(self, db: Database):
        self.db = db
        self.binance = BinanceCollector()
        self.reddit = RedditCollector()
        self.news = NewsCollector()
        self.onchain = OnChainCollector()
        self.status = {
            "binance": "INIT",
            "reddit": "INIT",
            "news": "INIT",
            "onchain": "INIT"
        }

    def run_once(self) -> dict:
        """Run all collectors once and return summary."""
        summary = {}
        with Progress() as progress:
            task1 = progress.add_task("[cyan]Collecting Binance data...", total=1)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.binance.run_once(self.db))
            progress.update(task1, advance=1)
            self.status["binance"] = "OK"

            task2 = progress.add_task("[magenta]Collecting Reddit data...", total=1)
            self.reddit.fetch_all(self.db)
            progress.update(task2, advance=1)
            self.status["reddit"] = "OK"

            task3 = progress.add_task("[yellow]Collecting News data...", total=1)
            self.news.run_once(self.db)
            progress.update(task3, advance=1)
            self.status["news"] = "OK"

            task4 = progress.add_task("[blue]Collecting On-chain data...", total=1)
            self.onchain.run_once(self.db)
            progress.update(task4, advance=1)
            self.status["onchain"] = "OK"

        return self.status

    def _price_loop(self, interval: int):
        while True:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.binance.run_once(self.db))
                self.status["binance"] = "OK"
            except Exception as e:
                logger.warning(f"Price loop error: {e}")
                self.status["binance"] = "ERROR"
            time.sleep(interval)

    def _sentiment_loop(self, interval: int):
        while True:
            try:
                self.reddit.fetch_all(self.db)
                self.status["reddit"] = "OK"
            except Exception as e:
                logger.warning(f"Reddit loop error: {e}")
                self.status["reddit"] = "ERROR"
            
            try:
                self.news.run_once(self.db)
                self.status["news"] = "OK"
            except Exception as e:
                logger.warning(f"News loop error: {e}")
                self.status["news"] = "ERROR"

            try:
                self.onchain.run_once(self.db)
                self.status["onchain"] = "OK"
            except Exception as e:
                logger.warning(f"On-chain loop error: {e}")
                self.status["onchain"] = "ERROR"
                
            time.sleep(interval)

    def run_continuous(self, price_interval=60, sentiment_interval=300):
        """Run collectors in background threads."""
        price_thread = threading.Thread(target=self._price_loop, args=(price_interval,), daemon=True)
        sentiment_thread = threading.Thread(target=self._sentiment_loop, args=(sentiment_interval,), daemon=True)
        
        price_thread.start()
        sentiment_thread.start()
        logger.info("Data pipeline threads started.")

    def get_status(self) -> dict:
        """Return status of collectors."""
        return self.status
