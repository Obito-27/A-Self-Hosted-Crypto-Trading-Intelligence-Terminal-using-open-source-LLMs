import logging
import os
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from storage.database import Database

logger = logging.getLogger(__name__)

class NewsCollector:
    CRYPTO_SOURCES = "coindesk.com,cointelegraph.com,decrypt.co,theblock.co"
    KEYWORDS = ["bitcoin", "ethereum", "crypto", "blockchain", "DeFi", "altcoin"]
    RSS_FEED_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("NEWS_API_KEY")
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

    def fetch_crypto_news(self, hours_back: int = 6) -> list:
        """Fetch from NewsAPI free tier."""
        if self.demo_mode or not self.api_key:
            return self.fetch_rss_fallback()

        url = "https://newsapi.org/v2/everything"
        from_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat()
        
        params = {
            "q": "crypto OR bitcoin OR ethereum",
            "from": from_time,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            logger.debug(f"NewsAPI status: {response.status}")
            if response.status_code == 200:
                return response.json().get("articles", [])
            else:
                logger.warning(f"NewsAPI failed: {response.status_code}. Falling back to RSS.")
                return self.fetch_rss_fallback()
        except Exception as e:
            logger.warning(f"Error calling NewsAPI: {e}. Falling back to RSS.")
            return self.fetch_rss_fallback()

    def fetch_rss_fallback(self) -> list:
        """Fallback: Parse CoinDesk RSS feed."""
        try:
            response = requests.get(self.RSS_FEED_URL)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                articles = []
                for item in root.findall(".//item"):
                    articles.append({
                        "title": item.find("title").text,
                        "description": item.find("description").text if item.find("description") is not None else "",
                        "url": item.find("link").text,
                        "publishedAt": item.find("pubDate").text,
                        "source": {"name": "CoinDesk RSS"}
                    })
                return articles
        except Exception as e:
            logger.error(f"RSS fallback failed: {e}")
        return []

    def run_once(self, db: Database) -> int:
        """Fetch news and store."""
        articles = self.fetch_crypto_news()
        total_stored = 0
        for art in articles:
            # Detect symbols in news (simple check)
            symbols = []
            text_to_check = f"{art['title']} {art.get('description', '')}".lower()
            if "bitcoin" in text_to_check or "btc" in text_to_check: symbols.append("BTC")
            if "ethereum" in text_to_check or "eth" in text_to_check: symbols.append("ETH")
            if "solana" in text_to_check or "sol" in text_to_check: symbols.append("SOL")
            
            if not symbols: symbols = ["BTC"] # Default
            
            for sym in symbols:
                db.insert_sentiment({
                    "source": "news",
                    "symbol": sym,
                    "text_snippet": art["title"][:200],
                    "sentiment_label": "PENDING",
                    "sentiment_score": 0.5,
                    "raw_text": f"{art['title']}\n{art.get('description', '')}"
                })
                total_stored += 1
        
        logger.info(f"News collection complete. Stored {total_stored} records.")
        return total_stored
