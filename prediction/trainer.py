import logging
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from storage.database import Database
from prediction.feature_engineering import FeatureEngineer
from prediction.xgboost_model import XGBoostPredictor

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, models_dir: str = "models/"):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.fe = FeatureEngineer()

    def train_all_symbols(self, db: Database, symbols: List[str] = ["BTC", "ETH", "SOL"]) -> dict:
        """Fetch data, build features, and train models for all symbols."""
        results = {}
        for symbol in symbols:
            logger.info(f"Starting training pipeline for {symbol}...")
            
            # 1. Load Data
            price_data = db.get_price_data(symbol, hours=24*90) # 3 months
            price_df = pd.DataFrame(price_data)
            
            # If insufficient data, use synthetic
            if len(price_df) < 500:
                logger.warning(f"Insufficient data for {symbol} ({len(price_df)} candles). Generating synthetic data...")
                price_df = self.generate_synthetic_training_data(symbol)
            
            # Load sentiment
            # (In a real scenario, we'd join sentiment records. For now, we use a mock sentiment_df if empty)
            sentiment_df = pd.DataFrame() # Simplified for hackathon
            
            # 2. Build Features
            features_df = self.fe.build_features(price_df, sentiment_df)
            features_df = self.fe.build_targets(features_df)
            
            # 3. Train
            predictor = XGBoostPredictor(symbol)
            summary = predictor.train(features_df)
            
            # 4. Save
            model_path = os.path.join(self.models_dir, f"{symbol}_model.joblib")
            predictor.save(model_path)
            
            results[symbol] = summary
            
        return results

    def generate_synthetic_training_data(self, symbol: str, candles: int = 8640) -> pd.DataFrame:
        """
        Generate realistic synthetic OHLCV using Geometric Brownian Motion.
        """
        start_prices = {'BTC': 45000, 'ETH': 2500, 'SOL': 100}
        S0 = start_prices.get(symbol, 100)
        mu = 0.0001
        sigma = 0.002
        dt = 1
        
        # GBM formula: S(t) = S(0) * exp((mu - 0.5*sigma^2)dt + sigma*sqrt(dt)*Z)
        returns = np.random.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), candles)
        price_path = S0 * np.exp(np.cumsum(returns))
        
        timestamps = [datetime.utcnow() - timedelta(minutes=15 * (candles - i)) for i in range(candles)]
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'symbol': symbol,
            'close': price_path,
            'volume': np.random.lognormal(mean=5, sigma=1, size=candles)
        })
        
        # Derived OHLC
        df['open'] = df['close'].shift(1).fillna(S0)
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.002, candles))
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.002, candles))
        
        return df

    def quick_train(self, db: Database, symbol: str = "BTC") -> dict:
        """Quick train for a single symbol."""
        return self.train_all_symbols(db, [symbol])
