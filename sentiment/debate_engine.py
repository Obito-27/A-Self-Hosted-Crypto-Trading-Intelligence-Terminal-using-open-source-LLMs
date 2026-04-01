import logging
import json
import os
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

class DebateEngine:
    DEFAULT_URL = "http://localhost:11434"
    MODEL = "mistral"

    PERSONAS = {
        "permabull": """You are 'The Permabull', an ultra-optimistic crypto trader. 
        Your goal is to find every possible bullish signal in the provided text. 
        Ignore the risks and focus on growth, adoption, and 'moon' potential.
        Keep your response to 2 sentences max. Be enthusiastic but analytical.""",
        
        "doomer": """You are 'The Doomer', a skeptical, risk-averse financial critic. 
        Your goal is to find every possible bearish signal, risk, or red flag in the provided text. 
        Focus on bubbles, regulatory crackdowns, and technical failures.
        Keep your response to 2 sentences max. Be critical and cautious."""
    }

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("OLLAMA_URL", self.DEFAULT_URL)

    def get_persona_opinion(self, persona: str, text: str) -> str:
        """Get opinion from a specific persona using Ollama."""
        system_prompt = self.PERSONAS.get(persona, "")
        payload = {
            "model": self.MODEL,
            "prompt": f"{system_prompt}\n\nAnalyzing this market data: \"{text}\"\n\nYour verdict:",
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.url}/api/generate", json=payload, timeout=15)
            if response.status_code == 200:
                return response.json().get("response", "No opinion available.")
        except Exception as e:
            logger.warning(f"Persona {persona} failed: {e}")
        
        return "Thinking... (Ollama not responding)"

    def conduct_debate(self, context_text: str) -> Dict[str, str]:
        """Run both personas against the same context."""
        return {
            "bull": self.get_persona_opinion("permabull", context_text),
            "bear": self.get_persona_opinion("doomer", context_text)
        }
