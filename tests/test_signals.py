from signals.generator import SignalGenerator, SignalType

class TestSignalGenerator:
    def setup_method(self):
        self.gen = SignalGenerator()
        
    def make_sentiment(self, score, label="BULLISH", confidence="HIGH"):
        return {"weighted_score": score, "label": label, 
                "confidence": confidence, "sample_count": 30}
    
    def make_prediction(self, direction_1h, conf_1h=0.7, direction_4h="UP"):
        return {
            "1h": {"direction": direction_1h, "confidence": conf_1h},
            "4h": {"direction": direction_4h, "confidence": 0.6},
            "24h": {"direction": "UP", "confidence": 0.55}
        }
    
    def test_strong_buy_signal(self):
        signal = self.gen.generate_signal(
            "BTC",
            self.make_sentiment(0.80, "BULLISH"),
            self.make_prediction("UP", 0.75),
            "ACCUMULATING",
            67000
        )
        assert signal.signal_type == SignalType.STRONG_BUY
        assert signal.confidence > 0.75
        
    def test_strong_sell_signal(self):
        # We need strength <= -3. 
        # Sent < 0.35 (-1)
        # Pred DOWN > 0.6 (-1)
        # Whale DISTRIBUTING (-1)
        signal = self.gen.generate_signal(
            "BTC",
            self.make_sentiment(0.20, "BEARISH"),
            self.make_prediction("DOWN", 0.75),
            "DISTRIBUTING",
            67000
        )
        assert signal.signal_type == SignalType.STRONG_SELL
        
    def test_hold_on_conflict(self):
        # Bullish sentiment (+1) but bearish prediction (-1) = HOLD (strength 0)
        signal = self.gen.generate_signal(
            "BTC",
            self.make_sentiment(0.80, "BULLISH"),
            self.make_prediction("DOWN", 0.75),
            "DISTRIBUTING", # (-1) -> Total -1 -> SELL (wait, let's check logic)
            67000
        )
        # strength: sent(+1), pred(-1), whale(-1) = -1 -> SELL? 
        # My implementation strength >= 2 is BUY, strength <= -2 is SELL. 
        # So -1 is HOLD.
        assert signal.signal_type == SignalType.HOLD
        
    def test_fud_forces_sell(self):
        signal = self.gen.generate_signal(
            "BTC",
            self.make_sentiment(0.80, "FUD"),  # FUD override
            self.make_prediction("UP", 0.90),
            "ACCUMULATING",
            67000
        )
        assert signal.signal_type == SignalType.SELL
        
    def test_reasoning_not_empty(self):
        signal = self.gen.generate_signal(
            "BTC",
            self.make_sentiment(0.75),
            self.make_prediction("UP"),
            "ACCUMULATING",
            67000
        )
        assert len(signal.reasoning) >= 2
