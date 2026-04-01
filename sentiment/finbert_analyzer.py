import logging
import re
from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from rich.progress import Progress

logger = logging.getLogger(__name__)

class FinBERTAnalyzer:
    MODEL_NAME = "ProsusAI/finbert"
    LABEL_MAP = {
        "positive": "BULLISH",
        "negative": "BEARISH", 
        "neutral": "NEUTRAL"
    }
    
    FUD_KEYWORDS = ["scam", "rug pull", "ponzi", "hack", "exit", "dead", "crash", "warning", "liquidation", "fake"]

    def __init__(self):
        self._pipeline = None

    def _load_model(self):
        if self._pipeline is None:
            logger.info("Loading FinBERT model...")
            self._pipeline = pipeline("sentiment-analysis", model=self.MODEL_NAME, tokenizer=self.MODEL_NAME)
            logger.info("FinBERT model loaded.")

    def preprocess_text(self, text: str) -> str:
        """Clean and truncate text for better analysis."""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Remove URLs
        text = re.sub(r'[\*\#\_]', '', text) # Remove Reddit markdown
        text = text.lower().strip()
        return text[:400] # Truncate

    def analyze(self, text: str) -> dict:
        """Analyze a single text snippet."""
        self._load_model()
        cleaned = self.preprocess_text(text)
        
        try:
            results = self._pipeline(cleaned, truncation=True, max_length=512)
            res = results[0]
            label = self.LABEL_MAP.get(res['label'], "NEUTRAL")
            score = res['score']
            
            # Check for FUD manually as an override or enhancement
            is_fud = self.classify_fud(cleaned)
            if is_fud:
                label = "FUD"
                score = max(0.8, score) # High confidence in FUD if keywords found

            return {
                "label": label,
                "score": score,
                "raw_label": res['label']
            }
        except Exception as e:
            logger.error(f"FinBERT analysis error: {e}")
            return {"label": "NEUTRAL", "score": 0.5, "raw_label": "neutral"}

    def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[dict]:
        """Analyze multiple texts efficiently."""
        self._load_model()
        cleaned_texts = [self.preprocess_text(t) for t in texts]
        results = []
        
        with Progress() as progress:
            task = progress.add_task("[green]Analyzing sentiment...", total=len(cleaned_texts))
            for i in range(0, len(cleaned_texts), batch_size):
                batch = cleaned_texts[i:i+batch_size]
                try:
                    batch_res = self._pipeline(batch, truncation=True, max_length=512)
                    for idx, res in enumerate(batch_res):
                        label = self.LABEL_MAP.get(res['label'], "NEUTRAL")
                        score = res['score']
                        if self.classify_fud(batch[idx]):
                            label = "FUD"
                            score = max(0.8, score)
                        results.append({"label": label, "score": score})
                except Exception as e:
                    logger.error(f"Batch analysis error at index {i}: {e}")
                    results.extend([{"label": "NEUTRAL", "score": 0.5}] * len(batch))
                progress.update(task, advance=len(batch))
        
        return results

    def classify_fud(self, text: str) -> bool:
        """Detect FUD patterns in text."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.FUD_KEYWORDS)

    def get_aggregate_sentiment(self, results: List[dict]) -> dict:
        """Aggregate results into a single score and summary."""
        if not results:
            return {"weighted_score": 0.5, "label": "NEUTRAL", "sample_count": 0, "confidence": "LOW"}
        
        counts = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0, "FUD": 0}
        total_score = 0
        
        for r in results:
            label = r['label']
            counts[label] += 1
            if label == "BULLISH":
                total_score += 1.0
            elif label == "NEUTRAL":
                total_score += 0.5
            elif label in ["BEARISH", "FUD"]:
                total_score += 0.0
        
        total = len(results)
        weighted_score = total_score / total
        
        # Determine dominant label
        max_label = max(counts, key=counts.get)
        
        # Confidence calculation
        max_pct = (counts[max_label] / total) * 100
        confidence = "HIGH" if max_pct > 70 else "MEDIUM" if max_pct > 55 else "LOW"
        
        return {
            "weighted_score": weighted_score,
            "label": max_label,
            "bullish_pct": (counts["BULLISH"] / total) * 100,
            "bearish_pct": (counts["BEARISH"] / total) * 100,
            "neutral_pct": (counts["NEUTRAL"] / total) * 100,
            "fud_pct": (counts["FUD"] / total) * 100,
            "sample_count": total,
            "confidence": confidence
        }
