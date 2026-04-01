import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)

class RiskScanner:
    RISK_CATEGORIES = {
        "REGULATORY": ["sec", "lawsuit", "ban", "regulation", "court", "compliance", "illegal"],
        "SECURITY": ["hack", "exploit", "breach", "vulnerability", "stolen", "drain"],
        "SYSTEMIC": ["depeg", "insolvent", "liquidation", "collapse", "bankrupt", "freeze"],
        "FRAUD": ["scam", "rug pull", "ponzi", "fake", "manipulation"]
    }

    def scan_text(self, text: str) -> List[Dict[str, str]]:
        """Identify specific risk categories in text."""
        found_risks = []
        text_lower = text.lower()
        
        for category, keywords in self.RISK_CATEGORIES.items():
            matches = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)]
            if matches:
                found_risks.append({
                    "category": category,
                    "severity": "HIGH" if category in ["SYSTEMIC", "SECURITY"] else "MEDIUM",
                    "keywords": matches
                })
        
        return found_risks

    def get_risk_summary(self, risk_reports: List[dict]) -> str:
        """Combine multiple risks into a dashboard summary."""
        if not risk_reports:
            return "✅ No systemic risks detected."
        
        counts = {}
        for r in risk_reports:
            cat = r["category"]
            counts[cat] = counts.get(cat, 0) + 1
            
        summary = "⚠️ RISK ALERT: " + ", ".join([f"{k} ({v})" for k, v in counts.items()])
        return summary
