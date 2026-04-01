import logging
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

logger = logging.getLogger(__name__)

class XGBoostPredictor:
    TIMEFRAMES = ["1h", "4h", "24h"]
    XGB_PARAMS = {
        "n_estimators": 300,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
        "gamma": 0.1,
        "random_state": 42,
        "n_jobs": -1
    }

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.models = {}
        self.encoders = {}
        self.feature_names = []
        self.trained = False

    def train(self, features_df: pd.DataFrame) -> dict:
        """Train models for each timeframe using cross-validation."""
        summary = {}
        
        # Prepare feature list (exclude targets and metadata)
        exclude = ['timestamp', 'symbol', 'id', 'open', 'high', 'low', 'close', 'volume', 'hour', 'day_of_week']
        target_cols = [f'target_{tf}' for tf in self.TIMEFRAMES]
        self.feature_names = [c for c in features_df.columns if c not in exclude and c not in target_cols]
        
        X = features_df[self.feature_names]
        
        for tf in self.TIMEFRAMES:
            target_col = f'target_{tf}'
            y_raw = features_df[target_col]
            
            # Filter rows with valid targets
            valid_idx = y_raw.notna()
            X_tf = X[valid_idx]
            y_tf_raw = y_raw[valid_idx]
            
            if len(X_tf) < 100:
                logger.warning(f"Insufficient data for {self.symbol} {tf} training.")
                continue

            le = LabelEncoder()
            y_tf = le.fit_transform(y_tf_raw)
            self.encoders[tf] = le
            
            # TimeSeriesSplit cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            scores = []
            
            for train_index, test_index in tscv.split(X_tf):
                X_train, X_test = X_tf.iloc[train_index], X_tf.iloc[test_index]
                y_train, y_test = y_tf[train_index], y_tf[test_index]
                
                model = xgb.XGBClassifier(**self.XGB_PARAMS)
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                scores.append(accuracy_score(y_test, preds))
            
            # Final model on all data
            final_model = xgb.XGBClassifier(**self.XGB_PARAMS)
            final_model.fit(X_tf, y_tf)
            self.models[tf] = final_model
            
            summary[tf] = {
                "accuracy": np.mean(scores),
                "cv_scores": scores,
                "feature_importance": self.get_feature_importance(tf)
            }
            logger.info(f"Trained {self.symbol} {tf} model. Avg Accuracy: {summary[tf]['accuracy']:.2f}")

        self.trained = True
        return summary

    def predict(self, features: pd.DataFrame) -> dict:
        """Make predictions for all timeframes."""
        if not self.trained:
            return {}
            
        results = {}
        X = features[self.feature_names].tail(1)
        
        for tf, model in self.models.items():
            probs = model.predict_proba(X)[0]
            pred_idx = np.argmax(probs)
            direction = self.encoders[tf].inverse_class_transform([pred_idx])[0] if hasattr(self.encoders[tf], 'inverse_class_transform') else self.encoders[tf].inverse_transform([pred_idx])[0]
            
            # Create prob map
            prob_map = {label: float(probs[i]) for i, label in enumerate(self.encoders[tf].classes_)}
            
            results[tf] = {
                "direction": direction,
                "confidence": float(probs[pred_idx]),
                "probabilities": prob_map
            }
            
        return results

    def get_feature_importance(self, timeframe: str = "1h", top_n: int = 10) -> dict:
        """Get feature importance from the model."""
        if timeframe not in self.models:
            return {}
        
        model = self.models[timeframe]
        importance = model.feature_importances_
        feat_imp = sorted(zip(self.feature_names, importance), key=lambda x: x[1], reverse=True)
        return {name: float(imp) for name, imp in feat_imp[:top_n]}

    def save(self, path: str):
        """Save state to file."""
        joblib.dump({
            "models": self.models,
            "encoders": self.encoders,
            "feature_names": self.feature_names,
            "symbol": self.symbol,
            "trained": self.trained
        }, path)

    @classmethod
    def load(cls, symbol: str, path: str):
        """Load state from file."""
        data = joblib.load(path)
        predictor = cls(symbol)
        predictor.models = data["models"]
        predictor.encoders = data["encoders"]
        predictor.feature_names = data["feature_names"]
        predictor.trained = data["trained"]
        return predictor
