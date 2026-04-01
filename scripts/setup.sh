#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p data

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
# Source command varies by OS, this is for bash
source venv/Scripts/activate || source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initializing database
echo "Initializing database..."
python -c "from storage.database import Database; Database('./data/crypto_terminal.db')"

# Download FinBERT model weights (cached)
echo "Downloading FinBERT weights (this may take a minute)..."
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')"

# Check for Ollama
if command -v ollama &> /dev/null
then
    echo "Ollama detected."
else
    echo "Ollama not found. If you want to use Llama 2/Mistral, please install it from https://ollama.ai"
fi

echo "------------------------------------------------"
echo "Setup complete! Run: streamlit run dashboard/app.py"
echo "------------------------------------------------"
