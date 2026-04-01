import logging
import random
import uuid
from datetime import datetime, timedelta
import numpy as np
from storage.database import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_random_walk(start_price, n_points, volatility=0.02):
    """Generates a random walk for price simulation."""
    prices = [start_price]
    for _ in range(n_points - 1):
        change = prices[-1] * random.uniform(-volatility, volatility)
        prices.append(max(1.0, prices[-1] + change))
    return prices

def seed():
    db = Database('./data/crypto_terminal.db')
    symbols = ['BTC', 'ETH', 'SOL']
    start_prices = {'BTC': 65000, 'ETH': 3500, 'SOL': 140}
    
    # 1. Generate 3 months of OHLCV data (15-min candles ~ 8640 points)
    logger.info("Generating synthetic price data...")
    n_points = 24 * 4 * 90 # 90 days
    end_time = datetime.utcnow()
    
    for symbol in symbols:
        prices = generate_random_walk(start_prices[symbol], n_points)
        records = []
        for i in range(n_points):
            timestamp = end_time - timedelta(minutes=15 * (n_points - i))
            price = prices[i]
            records.append({
                'symbol': symbol,
                'timestamp': timestamp,
                'open': price * (1 + random.uniform(-0.001, 0.001)),
                'high': price * (1 + random.uniform(0, 0.005)),
                'low': price * (1 - random.uniform(0, 0.005)),
                'close': price,
                'volume': random.uniform(100, 1000)
            })
        db.insert_price_data(records)

    # 2. Generate 200 synthetic sentiment records
    logger.info("Generating synthetic sentiment records...")
    sources = ['reddit', 'news']
    labels = ['BULLISH', 'BEARISH', 'NEUTRAL', 'FUD']
    
    for _ in range(200):
        symbol = random.choice(symbols)
        label = random.choice(labels)
        score = random.uniform(0.7, 1.0) if label == 'BULLISH' else random.uniform(0, 0.3) if label in ['BEARISH', 'FUD'] else random.uniform(0.4, 0.6)
        
        db.insert_sentiment({
            'source': random.choice(sources),
            'symbol': symbol,
            'text_snippet': f"Synthetic comment about {symbol} being {label}...",
            'sentiment_label': label,
            'sentiment_score': score,
            'raw_text': f"Full synthetic text for {symbol}. Market looks {label} today!"
        })

    # 3. Generate 20 synthetic whale transactions
    logger.info("Generating synthetic whale transactions...")
    directions = ['EXCHANGE_INFLOW', 'EXCHANGE_OUTFLOW', 'WALLET_TO_WALLET']
    
    for _ in range(20):
        db.insert_whale_tx({
            'tx_hash': f"0x{uuid.uuid4().hex}",
            'symbol': random.choice(['BTC', 'ETH']),
            'from_address': f"0x{uuid.uuid4().hex[:40]}",
            'to_address': f"0x{uuid.uuid4().hex[:40]}",
            'value_usd': random.uniform(1000000, 50000000),
            'direction': random.choice(directions),
            'timestamp': datetime.utcnow() - timedelta(hours=random.randint(0, 72))
        })

    logger.info("Seeding complete!")

if __name__ == "__main__":
    seed()
