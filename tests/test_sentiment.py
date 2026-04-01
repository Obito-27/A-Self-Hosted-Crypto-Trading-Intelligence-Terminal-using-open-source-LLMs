import pytest
from sentiment.finbert_analyzer import FinBERTAnalyzer
from sentiment.analyzer import SentimentAnalyzer

@pytest.fixture(scope="module")
def analyzer():
    return FinBERTAnalyzer()

class TestFinBERTAnalyzer:
    def test_bullish_text(self, analyzer):
        result = analyzer.analyze("Bitcoin is surging! All time highs incoming!")
        assert result["label"] == "BULLISH"
        assert result["score"] > 0.6
        
    def test_bearish_text(self, analyzer):
        result = analyzer.analyze("Crypto market crashing, massive sell off happening")
        assert result["label"] == "BEARISH"
        assert result["score"] > 0.6 # High confidence in bearishness
        
    def test_neutral_text(self, analyzer):
        result = analyzer.analyze("Bitcoin price is at $65,000 today")
        assert result["label"] == "NEUTRAL"
        
    def test_fud_detection(self, analyzer):
        # FinBERT might see this as neutral/negative, but our keyword filter should catch it
        result = analyzer.analyze("This token is a rug pull scam, developer ran away with funds")
        assert result["label"] == "FUD"
        
    def test_batch_processing(self, analyzer):
        texts = ["BTC going up", "ETH crashing", "SOL neutral"] * 10
        results = analyzer.analyze_batch(texts)
        assert len(results) == 30
        assert all("label" in r for r in results)
        
    def test_empty_text_handling(self, analyzer):
        # Should not crash on empty/weird inputs
        result = analyzer.analyze("")
        assert "label" in result
        result = analyzer.analyze("   ")
        assert "label" in result
        result = analyzer.analyze("🚀🚀🚀")  # emojis only
        assert "label" in result
