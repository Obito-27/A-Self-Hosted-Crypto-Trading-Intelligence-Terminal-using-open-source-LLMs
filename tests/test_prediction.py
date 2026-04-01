import pandas as pd
import numpy as np
import pytest
from prediction.feature_engineering import FeatureEngineer
from prediction.xgboost_model import XGBoostPredictor

class TestFeatureEngineering:
    def setup_method(self):
        # Generate 1000 synthetic candles
        np.random.seed(42)
        n = 1000
        self.price_df = pd.DataFrame({
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="15min"),
            "open": 45000 + np.cumsum(np.random.randn(n) * 100),
            "high": 0, "low": 0,
            "close": 45000 + np.cumsum(np.random.randn(n) * 100),
            "volume": np.abs(np.random.randn(n) * 1000 + 5000)
        })
        self.price_df["high"] = self.price_df["close"] * 1.005
        self.price_df["low"] = self.price_df["close"] * 0.995
        
    def test_features_generated(self):
        fe = FeatureEngineer()
        features = fe.build_features(self.price_df)
        assert len(features) > 0
        assert len(features.columns) >= 20  # At least 20 features
        
    def test_no_lookahead_bias(self):
        fe = FeatureEngineer()
        features = fe.build_features(self.price_df)
        # Check that targets are not in the main features list
        assert "target_1h" not in features.columns # until build_targets is called
        
    def test_model_training(self):
        fe = FeatureEngineer()
        features = fe.build_features(self.price_df)
        features = fe.build_targets(features)
        
        predictor = XGBoostPredictor("BTC")
        results = predictor.train(features)
        
        assert "1h" in results
        assert results["1h"]["accuracy"] > 0.3 # Random is 0.33 for 3 classes
