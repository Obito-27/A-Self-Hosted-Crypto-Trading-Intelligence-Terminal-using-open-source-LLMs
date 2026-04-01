import logging
import hashlib
from typing import Dict, Any, List
from sentiment.finbert_analyzer import FinBERTAnalyzer
from sentiment.ollama_analyzer import OllamaAnalyzer
from storage.database import Database
from sqlalchemy import text

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.finbert = FinBERTAnalyzer()
        self.ollama = OllamaAnalyzer()
        self._ollama_available = None
        self._cache = {}

    def analyze_text(self, text_str: str, use_ollama: bool = True) -> dict:
        """Analyze text using both models if available."""
        text_hash = hashlib.md5(text_str.encode()).hexdigest()
        if text_hash in self._cache:
            return self._cache[text_hash]

        # 1. Run FinBERT (Reliable baseline)
        finbert_res = self.finbert.analyze(text_str)
        
        result = {
            "label": finbert_res["label"],
            "score": finbert_res["score"],
            "narrative": f"Detected {finbert_res['label']} sentiment via FinBERT.",
            "fud": finbert_res["label"] == "FUD"
        }

        # 2. Check Ollama availability once
        if self._ollama_available is None:
            self._ollama_available = self.ollama.is_available()

        # 3. Enhance with Ollama if available
        if use_ollama and self._ollama_available:
            ollama_res = self.ollama.analyze(text_str)
            if ollama_res:
                # We trust FinBERT's score more for quantitative models, 
                # but Ollama's narrative is much better.
                result["narrative"] = ollama_res.get("narrative", result["narrative"])
                if ollama_res.get("fud"):
                    result["label"] = "FUD"
                    result["fud"] = True

        self._cache[text_hash] = result
        return result

    def analyze_pending(self, db: Database) -> int:
        """Analyze all records with PENDING status."""
        query = text("SELECT id, raw_text FROM sentiment_records WHERE sentiment_label = 'PENDING'")
        pending = []
        try:
            with db.engine.connect() as conn:
                result = conn.execute(query)
                pending = [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error fetching pending sentiment: {e}")
            return 0

        if not pending:
            return 0

        logger.info(f"Analyzing {len(pending)} pending sentiment records...")
        
        count = 0
        # Use batch processing for FinBERT
        ids = [p['id'] for p in pending]
        texts = [p['raw_text'] for p in pending]
        
        # We can't easily batch the mixed logic, so we do it record by record for now
        # but FinBERT will be fast due to internal caching of the pipeline
        for item in pending:
            res = self.analyze_text(item['raw_text'])
            update_query = text("""
                UPDATE sentiment_records 
                SET sentiment_label = :label, sentiment_score = :score
                WHERE id = :id
            """)
            try:
                with db.engine.connect() as conn:
                    conn.execute(update_query, {
                        "label": res["label"],
                        "score": res["score"],
                        "id": item["id"]
                    })
                    conn.commit()
                count += 1
            except Exception as e:
                logger.error(f"Error updating sentiment record {item['id']}: {e}")

        return count

    def get_coin_sentiment(self, db: Database, symbol: str, hours: int = 6) -> dict:
        """Get aggregated sentiment for a symbol."""
        since = (db.get_recent_sentiment(symbol, hours))
        # Note: Database.get_recent_sentiment returns simplified aggregation.
        # We could also fetch all recent results and use FinBERTAnalyzer.get_aggregate_sentiment
        
        query = text("""
            SELECT sentiment_label as label, sentiment_score as score 
            FROM sentiment_records 
            WHERE symbol = :symbol AND created_at >= datetime('now', '-:hours hours')
            AND sentiment_label != 'PENDING'
        """)
        try:
            with db.engine.connect() as conn:
                rows = conn.execute(query, {"symbol": symbol, "hours": hours}).fetchall()
                results = [{"label": r[0], "score": r[1]} for r in rows]
                return self.finbert.get_aggregate_sentiment(results)
        except Exception as e:
            logger.error(f"Error calculating aggregate sentiment: {e}")
            return {"weighted_score": 0.5, "label": "NEUTRAL", "sample_count": 0, "confidence": "LOW"}
