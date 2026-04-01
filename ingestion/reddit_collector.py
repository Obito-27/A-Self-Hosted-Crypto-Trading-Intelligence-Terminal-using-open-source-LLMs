import logging
import os
import time
from datetime import datetime, timedelta
import praw
from dotenv import load_dotenv
from storage.database import Database

logger = logging.getLogger(__name__)

class RedditCollector:
    SUBREDDITS = [
        "cryptocurrency", "Bitcoin", "ethereum", "solana", 
        "CryptoMarkets", "altcoin"
    ]
    COIN_KEYWORDS = {
        "BTC": ["bitcoin", "btc", "$btc"],
        "ETH": ["ethereum", "eth", "$eth", "ether"],
        "SOL": ["solana", "sol", "$sol"],
        "BNB": ["binance", "bnb", "$bnb"],
        "ADA": ["cardano", "ada", "$ada"]
    }
    
    FALLBACK_POSTS = [
        {"text": "Bitcoin breaking all time highs! This bull run is just getting started!", "symbol": "BTC"},
        {"text": "ETH 2.0 staking rewards are incredible. Accumulating more ethereum.", "symbol": "ETH"},
        {"text": "SOL network going down again. Starting to lose faith in Solana.", "symbol": "SOL"},
        {"text": "Is Cardano dead? No updates for months. ADA price dropping.", "symbol": "ADA"},
        {"text": "Binance is the king of exchanges. BNB to the moon!", "symbol": "BNB"},
        {"text": "Regulatory FUD is hitting Bitcoin hard today. Expecting a dip.", "symbol": "BTC"},
        {"text": "Ethereum gas fees are way too high. Switching to Solana for DeFi.", "symbol": "ETH"},
        {"text": "SOL ecosystem growing so fast. NFT volume is crazy.", "symbol": "SOL"},
        {"text": "ADA staking is so easy. Long term hold for me.", "symbol": "ADA"},
        {"text": "Market is looking neutral. Waiting for BTC to break resistance.", "symbol": "BTC"}
    ]

    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "crypto-terminal-v1")
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        self.reddit = None
        if not self.demo_mode and self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("Reddit client initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize Reddit client: {e}. Falling back to demo mode.")
                self.demo_mode = True
        else:
            self.demo_mode = True
            logger.info("Reddit collector running in DEMO_MODE.")

    def fetch_hot_posts(self, subreddit_name: str, limit: int = 25) -> list:
        """Fetch hot posts from a subreddit."""
        if self.demo_mode or not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            for post in subreddit.hot(limit=limit):
                # Only last 6 hours
                if (time.time() - post.created_utc) < (6 * 3600):
                    posts.append({
                        'title': post.title,
                        'selftext': post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc
                    })
            return posts
        except Exception as e:
            logger.warning(f"Error fetching from r/{subreddit_name}: {e}")
            return []

    def detect_coins(self, text: str) -> list:
        """Detect which coins are mentioned in the text."""
        detected = []
        text_lower = text.lower()
        for symbol, keywords in self.COIN_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(symbol)
        return detected

    def fetch_all(self, db: Database) -> int:
        """Fetch from all subreddits, detect coins, and store."""
        total_collected = 0
        
        if self.demo_mode:
            logger.info("Using fallback Reddit posts for demo mode.")
            for post in self.FALLBACK_POSTS:
                db.insert_sentiment({
                    'source': 'reddit',
                    'symbol': post['symbol'],
                    'text_snippet': post['text'][:200],
                    'sentiment_label': 'PENDING',
                    'sentiment_score': 0.5,
                    'raw_text': post['text']
                })
            return len(self.FALLBACK_POSTS)

        for sub in self.SUBREDDITS:
            posts = self.fetch_hot_posts(sub)
            for post in posts:
                full_text = f"{post['title']}\n{post['selftext']}"
                coins = self.detect_coins(full_text)
                
                # If no specific coin detected, could default to BTC or ignore
                if not coins: continue
                
                for coin in coins:
                    db.insert_sentiment({
                        'source': 'reddit',
                        'symbol': coin,
                        'text_snippet': post['title'][:200],
                        'sentiment_label': 'PENDING', # Will be updated by sentiment analyzer
                        'sentiment_score': 0.5,
                        'raw_text': full_text
                    })
                    total_collected += 1
        
        logger.info(f"Reddit collection complete. Found {total_collected} posts.")
        return total_collected

    def run_continuous(self, db: Database, interval_seconds: int = 300):
        """Continuous loop for Reddit fetching."""
        while True:
            self.fetch_all(db)
            time.sleep(interval_seconds)
