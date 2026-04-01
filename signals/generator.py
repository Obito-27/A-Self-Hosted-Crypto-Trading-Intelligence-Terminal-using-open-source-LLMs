import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from typing import List, Dict, Any, Optional
from storage.database import Database
from sentiment.analyzer import SentimentAnalyzer
from prediction.predictor import LivePredictor
from ingestion.onchain_collector import OnChainCollector

logger = logging.getLogger(__name__)

class SignalType(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    confidence: float
    sentiment_score: float
    price_prediction_1h: str
    price_confidence_1h: float
    price_prediction_4h: str
    price_confidence_4h: float
    whale_signal: str
    current_price: float
    reasoning: List[str]
    signal_strength: int
    timestamp: datetime

class SignalGenerator:
    def generate_signal(
        self,
        symbol: str,
        sentiment: dict,
        prediction: dict,
        whale_signal: str,
        current_price: float
    ) -> TradingSignal:
        """
        Main signal logic combining sentiment, ML prediction and whale data.
        """
        reasons = []
        strength = 0
        
        sent_score = sentiment.get("weighted_score", 0.5)
        pred_1h = prediction.get("1h", {"direction": "SIDEWAYS", "confidence": 0.5})
        pred_4h = prediction.get("4h", {"direction": "SIDEWAYS", "confidence": 0.5})
        
        # 1. Sentiment Factor
        if sent_score > 0.65:
            reasons.append(f"Strong bullish sentiment ({sent_score:.2f})")
            strength += 1
        elif sent_score < 0.35:
            reasons.append(f"Strong bearish sentiment ({sent_score:.2f})")
            strength -= 1
            
        # 2. Prediction Factor
        if pred_1h["direction"] == "UP" and pred_1h["confidence"] > 0.6:
            reasons.append(f"1h ML Model predicts UP ({pred_1h['confidence']:.2f})")
            strength += 1
        elif pred_1h["direction"] == "DOWN" and pred_1h["confidence"] > 0.6:
            reasons.append(f"1h ML Model predicts DOWN ({pred_1h['confidence']:.2f})")
            strength -= 1
            
        # 3. Whale Factor
        if whale_signal == "ACCUMULATING":
            reasons.append("Whale accumulation detected on-chain")
            strength += 1
        elif whale_signal == "DISTRIBUTING":
            reasons.append("Whale distribution detected on-chain")
            strength -= 1

        # Determine Signal Type
        final_type = SignalType.HOLD
        confidence = 0.5
        
        if strength >= 3:
            final_type = SignalType.STRONG_BUY
            confidence = (sent_score + pred_1h["confidence"] + 0.8) / 3
        elif strength >= 2:
            final_type = SignalType.BUY
            confidence = (sent_score + pred_1h["confidence"]) / 2
        elif strength <= -3:
            final_type = SignalType.STRONG_SELL
            confidence = ((1-sent_score) + pred_1h["confidence"] + 0.8) / 3
        elif strength <= -2:
            final_type = SignalType.SELL
            confidence = ((1-sent_score) + pred_1h["confidence"]) / 2

        # Override Rules
        if sentiment.get("label") == "FUD":
            final_type = SignalType.SELL
            reasons.append("OVERRIDE: Market FUD detected")
            confidence = 0.9
            
        if sentiment.get("confidence") == "LOW" and final_type != SignalType.HOLD:
            reasons.append("DOWNGRADE: Low sentiment confidence")
            final_type = SignalType.HOLD
            confidence = 0.4

        return TradingSignal(
            symbol=symbol,
            signal_type=final_type,
            confidence=min(1.0, confidence),
            sentiment_score=sent_score,
            price_prediction_1h=pred_1h["direction"],
            price_confidence_1h=pred_1h["confidence"],
            price_prediction_4h=pred_4h["direction"],
            price_confidence_4h=pred_4h["confidence"],
            whale_signal=whale_signal,
            current_price=current_price,
            reasoning=reasons,
            signal_strength=abs(strength),
            timestamp=datetime.utcnow()
        )

    def generate_all(self, db: Database, predictor: LivePredictor, analyzer: SentimentAnalyzer, onchain: OnChainCollector) -> List[TradingSignal]:
        """Generate signals for all symbols and save to DB."""
        symbols = ["BTC", "ETH", "SOL"]
        signals = []
        
        # Analyze pending sentiment first
        analyzer.analyze_pending(db)
        
        for symbol in symbols:
            try:
                sentiment = analyzer.get_coin_sentiment(db, symbol)
                prediction = predictor.predict_now(db, symbol)
                
                # Simplified whale signal from db
                txs = db.get_whale_txs(hours=4)
                inflows = sum(1 for tx in txs if tx['direction'] == "EXCHANGE_INFLOW")
                outflows = sum(1 for tx in txs if tx['direction'] == "EXCHANGE_OUTFLOW")
                whale_sig = "ACCUMULATING" if outflows > inflows else "DISTRIBUTING" if inflows > outflows else "NEUTRAL"
                
                # Get current price from latest OHLCV
                price_data = db.get_price_data(symbol, hours=1)
                current_price = price_data[-1]['close'] if price_data else 0.0
                
                signal = self.generate_signal(symbol, sentiment, prediction, whale_sig, current_price)
                
                # Save to DB
                db.insert_signal({
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type.value,
                    "confidence": signal.confidence,
                    "sentiment_score": signal.sentiment_score,
                    "price_prediction": signal.price_prediction_1h,
                    "onchain_signal": signal.whale_signal,
                    "reasoning": json.dumps(signal.reasoning)
                })
                
                signals.append(signal)
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {e}")
                
        return signals
