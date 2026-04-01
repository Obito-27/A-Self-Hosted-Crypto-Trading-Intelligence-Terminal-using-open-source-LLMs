"""
Run this BEFORE the hackathon to cache model weights.
This prevents download delays during the demo.
"""
print("Pre-downloading FinBERT model (~500MB)...")
from transformers import AutoTokenizer, AutoModelForSequenceClassification
AutoTokenizer.from_pretrained("ProsusAI/finbert")
AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
print("✅ FinBERT cached")

print("Pre-downloading Prophet...")
from prophet import Prophet
# Prophet doesn't need explicit download but this ensures it's initialized
print("✅ Prophet ready")

print("All models ready! You can now run offline.")
