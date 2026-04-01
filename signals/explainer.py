from signals.generator import TradingSignal, SignalType
from rich.markup import escape

class SignalExplainer:
    def explain_signal(self, signal: TradingSignal) -> str:
        """Generate a 3-4 sentence narrative explanation."""
        type_str = signal.signal_type.value.replace("_", " ")
        direction_map = {"UP": "upward", "DOWN": "downward", "SIDEWAYS": "sideways"}
        
        narrative = f"{signal.symbol} is showing {type_str} conditions as of {signal.timestamp.strftime('%H:%M')} UTC. "
        
        # Sentiment part
        sent_desc = "bullish" if signal.sentiment_score > 0.6 else "bearish" if signal.sentiment_score < 0.4 else "neutral"
        narrative += f"Sentiment analysis shows {sent_desc} momentum (score: {signal.sentiment_score:.2f}). "
        
        # Prediction part
        pred_dir = direction_map.get(signal.price_prediction_1h, "stable")
        narrative += f"Our XGBoost model predicts a {signal.price_confidence_1h*100:.0f}% probability of {pred_dir} movement in the next hour. "
        
        # Whale part
        if signal.whale_signal != "NEUTRAL":
            narrative += f"On-chain data confirms whale {signal.whale_signal.lower()} activity. "
            
        narrative += f"Overall signal strength: {signal.signal_strength}/5."
        
        return narrative

    def format_for_terminal(self, signal: TradingSignal) -> str:
        """Format signal using rich markup."""
        color = "green" if "BUY" in signal.signal_type.value else "red" if "SELL" in signal.signal_type.value else "yellow"
        
        output = f"[{color} bold]{signal.signal_type.value}[/{color} bold] for [cyan]{signal.symbol}[/cyan] @ ${signal.current_price:,.2f}\n"
        output += f"Confidence: {signal.confidence:.2%}\n"
        output += "Reasoning:\n"
        for r in signal.reasoning:
            output += f" - {r}\n"
        
        return output

    def format_for_dashboard(self, signal: TradingSignal) -> dict:
        """Format signal as dict for Streamlit."""
        return {
            "symbol": signal.symbol,
            "type": signal.signal_type.value,
            "confidence": f"{signal.confidence:.1%}",
            "price": f"${signal.current_price:,.2f}",
            "explanation": self.explain_signal(signal),
            "strength": signal.signal_strength
        }
