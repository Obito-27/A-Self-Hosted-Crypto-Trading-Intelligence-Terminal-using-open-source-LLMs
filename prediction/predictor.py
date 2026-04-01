import logging
import os
import pandas as pd
from typing import List, Dict, Optional
from storage.database import Database
from prediction.feature_engineering import FeatureEngineer
from prediction.xgboost_model import XGBoostPredictor

logger = logging.getLogger(__name__)

class LivePredictor:
    def __init__(self, models_dir: str = "models/"):
        self.models_dir = models_dir
        self.predictors = {}
        self.fe = FeatureEngineer()

    def load_models(self, symbols: List[str]):
        """Load saved models from disk."""
        for symbol in symbols:
            model_path = os.path.join(self.models_dir, f"{symbol}_model.joblib")
            if os.path.exists(model_path):
                try:
                    self.predictors[symbol] = XGBoostPredictor.load(symbol, model_path)
                    logger.info(f"Loaded model for {symbol}")
                except Exception as e:
                    logger.error(f"Error loading model for {symbol}: {e}")
            else:
                logger.warning(f"No model found for {symbol} at {model_path}")

    def predict_now(self, db: Database, symbol: str) -> dict:
        """Fetch latest data and return prediction."""
        if symbol not in self.predictors:
            return {}
            
        # Get enough history for indicators (ADX/RSI/EMAs need ~50-100 candles)
        price_data = db.get_price_data(symbol, hours=48)
        if not price_data:
            return {}
            
        price_df = pd.DataFrame(price_data)
        
        # Build features for the latest candle
        features_df = self.fe.build_features(price_df)
        
        # Predict
        prediction = self.predictors[symbol].predict(features_df)
        
        # Add feature importance for the 1h timeframe
        prediction["feature_importance"] = self.predictors[symbol].get_feature_importance("1h")
        
        return prediction

    def predict_all(self, db: Database) -> dict:
        """Run predictions for all loaded symbols."""
        results = {}
        for symbol in self.predictors.keys():
            results[symbol] = self.predict_now(db, symbol)
        return results
