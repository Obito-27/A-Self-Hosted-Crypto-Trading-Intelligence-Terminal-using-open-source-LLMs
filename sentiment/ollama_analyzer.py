import logging
import requests
import json
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class OllamaAnalyzer:
    DEFAULT_URL = "http://localhost:11434"
    MODEL = "mistral"
    
    SYSTEM_PROMPT = """You are a crypto market sentiment analyst. Analyze the given text and respond with ONLY a JSON object.

Examples:
Input: "Bitcoin just broke $70k! This bull run is insane, accumulating more BTC"
Output: {"label": "BULLISH", "score": 0.92, "narrative": "Strong bullish momentum, accumulation behavior", "fud": false}

Input: "Another exchange got hacked. Billions lost. Crypto is a scam, everyone will lose money"
Output: {"label": "FUD", "score": 0.05, "narrative": "Fear-driven content, exchange hack narrative", "fud": true}

Input: "ETH gas fees are high today. Network congestion due to NFT minting."
Output: {"label": "NEUTRAL", "score": 0.5, "narrative": "Factual network observation, no directional bias", "fud": false}

Input: "Whales are dumping. Smart money is leaving. This looks like the top."
Output: {"label": "BEARISH", "score": 0.15, "narrative": "Distribution signals, bearish whale activity narrative", "fud": false}

RULES:
- label must be exactly: BULLISH, BEARISH, NEUTRAL, or FUD
- score: 0.0 (max bearish) to 1.0 (max bullish), 0.5 = neutral
- narrative: max 15 words explaining the key signal
- fud: true only for panic/scam/fear narratives
- Respond ONLY with the JSON object, nothing else"""

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("OLLAMA_URL", self.DEFAULT_URL)

    def is_available(self) -> bool:
        """Check if Ollama server is running and model is pulled."""
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                return any(self.MODEL in m for m in models)
        except:
            return False
        return False

    def analyze(self, text: str) -> Optional[dict]:
        """Analyze text using Ollama."""
        payload = {
            "model": self.MODEL,
            "prompt": f"{self.SYSTEM_PROMPT}\n\nInput: \"{text}\"\nOutput:",
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(f"{self.url}/api/generate", json=payload, timeout=10)
            if response.status_code == 200:
                result_text = response.json().get("response", "{}")
                return json.loads(result_text)
        except Exception as e:
            logger.warning(f"Ollama analysis failed: {e}")
        return None

    def analyze_batch(self, texts: List[str]) -> List[Optional[dict]]:
        """Analyze a batch of texts (synchronously for now)."""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results
