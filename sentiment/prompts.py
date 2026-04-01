import logging
from rich.console import Console
from rich.table import Table
from typing import List, Dict

logger = logging.getLogger(__name__)
console = Console()

VALIDATION_SET = [
    {
        "text": "Just bought more BTC. The halving is coming and institutions are buying.",
        "expected_label": "BULLISH",
        "expected_score_range": (0.65, 1.0)
    },
    {
        "text": "Ethereum transaction failed again. High gas fees making it unusable for small users.",
        "expected_label": "BEARISH",
        "expected_score_range": (0.0, 0.45)
    },
    {
        "text": "Crypto market open as usual. Some coins up, some down.",
        "expected_label": "NEUTRAL",
        "expected_score_range": (0.35, 0.65)
    },
    {
        "text": "WARNING: This new token is a total rug pull. Dev wallet holds 90%. DO NOT BUY.",
        "expected_label": "FUD",
        "expected_score_range": (0.0, 0.2)
    },
    {
        "text": "Bitcoin price stabilizes as market awaits Fed decision on interest rates.",
        "expected_label": "NEUTRAL",
        "expected_score_range": (0.4, 0.6)
    },
    {
        "text": "Solana ecosystem sees massive growth in developer activity and new dApps.",
        "expected_label": "BULLISH",
        "expected_score_range": (0.7, 1.0)
    },
    {
        "text": "Major security breach detected in popular DeFi protocol. Assets at risk.",
        "expected_label": "FUD",
        "expected_score_range": (0.0, 0.3)
    },
    {
        "text": "Technical indicators suggest a significant correction for ETH in the short term.",
        "expected_label": "BEARISH",
        "expected_score_range": (0.0, 0.4)
    },
    {
        "text": "New partnership announced between Binance and major payment processor.",
        "expected_label": "BULLISH",
        "expected_score_range": (0.6, 1.0)
    },
    {
        "text": "The crypto market capitalization remained relatively flat over the weekend.",
        "expected_label": "NEUTRAL",
        "expected_score_range": (0.4, 0.6)
    }
]

def validate_analyzer(analyzer):
    """
    Run analyzer against VALIDATION_SET and print results.
    """
    correct = 0
    total = len(VALIDATION_SET)
    results = []

    table = Table(title="Sentiment Analyzer Validation")
    table.add_column("Text Snippet", style="cyan", no_wrap=True)
    table.add_column("Expected", style="magenta")
    table.add_column("Actual", style="green")
    table.add_column("Score", justify="right")
    table.add_column("Status", justify="center")

    for item in VALIDATION_SET:
        res = analyzer.analyze_text(item["text"], use_ollama=False) # Test base FinBERT
        
        is_correct = res["label"] == item["expected_label"]
        if is_correct:
            correct += 1
        
        status = "✅" if is_correct else "❌"
        results.append({
            "text": item["text"],
            "expected": item["expected_label"],
            "actual": res["label"],
            "score": res["score"],
            "correct": is_correct
        })
        
        table.add_row(
            item["text"][:40] + "...",
            item["expected_label"],
            res["label"],
            f"{res['score']:.2f}",
            status
        )

    accuracy = (correct / total) * 100
    console.print(table)
    console.print(f"\n[bold]Overall Accuracy: {accuracy:.1f}% ({correct}/{total})[/bold]\n")
    
    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "details": results
    }
