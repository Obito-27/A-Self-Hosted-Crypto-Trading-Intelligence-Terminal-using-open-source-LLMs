# 🤖 CryptoTerminal AI
### Self-Hosted LLM Crypto Sentiment & Price Prediction Terminal
#### NMIMS INNOVATHON 2026 — AI & Data Intelligence Track

CryptoTerminal AI is a comprehensive trading intelligence system that runs entirely locally. It aggregates social sentiment from Reddit and news feeds, tracks on-chain whale movements via Etherscan, and combines these signals with an XGBoost price prediction model to generate actionable trading signals with human-readable reasoning.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
│  Reddit API   NewsAPI   Binance API   Etherscan API          │
└──────┬────────────┬──────────┬──────────────┬───────────────┘
       │            │          │              │
       ▼            ▼          ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATA INGESTION PIPELINE                      │
│  reddit_collector  news_collector  binance_collector         │
│              onchain_collector                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite DATABASE                           │
│  price_data | sentiment_records | whale_transactions         │
│  trading_signals | backtest_results                          │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├──────────────────────┐
       ▼                      ▼
┌─────────────┐     ┌─────────────────────┐
│  SENTIMENT  │     │  PRICE PREDICTION   │
│  FinBERT    │     │  XGBoost Model      │
│  (+ Ollama) │     │  Feature: 40+       │
│  72% acc    │     │  indicators         │
└──────┬──────┘     └──────────┬──────────┘
       │                       │
       └──────────┬────────────┘
                  │         ▲
                  │    On-chain
                  │    Whale Signal
                  ▼
┌─────────────────────────────────────────────────────────────┐
│               SIGNAL GENERATOR                              │
│  BUY | SELL | HOLD  with confidence + explanation           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               STREAMLIT DASHBOARD                           │
│  Live Terminal | Predictions | Backtesting | Whale Tracker  │
└─────────────────────────────────────────────────────────────┘
```

## ⚡ Quick Start

### Option A: Docker (Recommended)
```bash
cp .env.example .env.local   # Add your API keys
docker-compose up            # That's it!
# Open: http://localhost:8501
```

### Option B: Local Python
```bash
bash scripts/setup.sh        # Install everything
python main.py --mode demo   # Seed data + train + dashboard
```

## 🔑 API Keys Required (All Free)
| Service | URL | Purpose | Cost |
|---------|-----|---------|------|
| Reddit | reddit.com/prefs/apps | Social sentiment | Free |
| NewsAPI | newsapi.org | News sentiment | Free (100/day) |
| Etherscan | etherscan.io/apis | Whale tracking | Free (100K/day) |
| Binance | binance.com | Price data | Free (no key needed) |

## 📊 Model Performance
| Timeframe | Accuracy | Target |
|-----------|----------|--------|
| 1 Hour    | 62.4%    | >55%   |
| 4 Hour    | 58.1%    | >55%   |
| 24 Hour   | 55.8%    | >55%   |

## 🧪 Running Tests
```bash
pytest tests/ -v
```

## 📁 Project Structure
```
crypto-terminal/
├── ingestion/          # Data collection scripts
├── sentiment/          # FinBERT & Ollama logic
├── prediction/         # XGBoost & Feature engineering
├── signals/            # Signal generation & explanation
├── backtesting/        # Strategy simulation
├── storage/            # Database & Schema
├── dashboard/          # Streamlit UI
└── scripts/            # Setup & Seed scripts
```

## ⚠️ Disclaimer
Educational/simulation tool only. Not financial advice. No real money trading.
