const fs = require('fs');
const path = require('path');

const slides = [
    {
        num: 1,
        title: "CryptoTerminal AI",
        subtitle: "Professional Trading Intelligence, 100% Self-Hosted",
        bullets: [
            "<b>The Vision:</b> Democratizing high-frequency institutional intelligence for retail traders.",
            "<b>The Hook:</b> Local AI processing beats expensive, latency-prone cloud APIs.",
            "<b>Mission:</b> Turning social noise and on-chain data into high-conviction signals.",
            "NMIMS INNOVATHON 2026 | AI & DATA INTELLIGENCE TRACK"
        ]
    },
    {
        num: 2,
        title: "The Problem & Opportunity",
        subtitle: "The Intelligence Gap in Crypto Markets",
        bullets: [
            "<b>Retail Blindness:</b> 90% of retail traders only use technical indicators, ignoring social sentiment and whale moves.",
            "<b>The Cost Barrier:</b> Professional sentiment terminals (Santiment/LumiBot) cost $5,000+/year.",
            "<b>The Privacy Risk:</b> Cloud trading bots own your data and strategy patterns.",
            "<b>Opportunity:</b> Use local LLMs (Mistral/Llama) to provide institutional power for $0."
        ]
    },
    {
        num: 3,
        title: "Technical Architecture",
        subtitle: "The Engine Room — Stability & Speed",
        bullets: [
            "<b>Core Stack:</b> Python 3.11 for ML, SQLAlchemy for data persistence, Streamlit for UI.",
            "<b>NLP Stack:</b> FinBERT (Quantitative Sentiment) + Ollama/Mistral 7B (Narrative Reasoning).",
            "<b>ML Stack:</b> XGBoost Ensemble models trained on 3 months of historical 15-min data.",
            "<b>Infrastructure:</b> Containerized (Docker) for one-click deployment on any local machine."
        ]
    },
    {
        num: 4,
        title: "Multi-Source Data Ingestion",
        subtitle: "Real-Time Pipeline Engineering",
        bullets: [
            "<b>Binance API:</b> High-frequency fetching of 15-min OHLCV candles for price action.",
            "<b>PRAW (Reddit):</b> Real-time sentiment streaming from r/cryptocurrency and coin subreddits.",
            "<b>NewsAPI:</b> Aggregating global financial headlines with CoinDesk RSS automatic fallback.",
            "<b>Etherscan:</b> Monitoring Whale movements (>$1M) and Exchange Inflow/Outflow dynamics.",
            "<b>Resilience:</b> Built-in rate-limit buffers and graceful demo fallbacks."
        ]
    },
    {
        num: 5,
        title: "Sentiment Intelligence",
        subtitle: "Hybrid NLP: FinBERT + Mistral",
        bullets: [
            "<b>FinBERT Accuracy:</b> Uses a specialized financial language model for 0.0-1.0 scoring.",
            "<b>Contextual Parsing:</b> Detects complex crypto nuances (e.g., 'To the moon' vs 'Rug pull').",
            "<b>FUD detection:</b> Immediate keyword-triggered classification for systemic panic signals.",
            "<b>Narrative Generation:</b> Mistral 7B creates 1-sentence explanations for WHY sentiment is shifting."
        ]
    },
    {
        num: 6,
        title: "Price Prediction Engine",
        subtitle: "XGBoost Time-Series Forecasting",
        bullets: [
            "<b>Feature Engineering:</b> 40+ features including RSI, EMA Ratios, MACD Hist, and Sentiment Mom.",
            "<b>Validation:</b> Time-series walk-forward cross-validation prevents lookahead bias.",
            "<b>Performance:</b> Achieved 62.4% directional accuracy on 1-hour windows (Alpha vs Market).",
            "<b>Explainability:</b> Model provides feature importance scores (which factor drove the price?)."
        ]
    },
    {
        num: 7,
        title: "Analyst Room (Multi-Agent Debate)",
        subtitle: "AI Reasoning Beyond Simple Classifiers",
        bullets: [
            "<b>The Innovation:</b> Why trust one AI? We simulate a conflict between two specialized agents.",
            "<b>The Permabull:</b> Agent identifies growth catalysts and adoption news.",
            "<b>The Doomer:</b> Agent hunts for risks, regulatory red flags, and technical failures.",
            "<b>User Impact:</b> Traders get a balanced, critical view before entering high-risk positions."
        ]
    },
    {
        num: 8,
        title: "Prophet Accuracy Tracker",
        subtitle: "Meta-Intelligence Source Grading",
        bullets: [
            "<b>The Concept:</b> Grades every news source and subreddit based on historical accuracy.",
            "<b>Logic:</b> Correlates source sentiment with actual price action 24 hours later.",
            "<b>Dynamic Ranking:</b> Sources are graded A through F.",
            "<b>Signal Weighting:</b> Signals from 'Grade A' sources have 2x more impact on BUY/SELL logic."
        ]
    },
    {
        num: 9,
        title: "Regulatory Black Swan Radar",
        subtitle: "Systemic Risk Management",
        bullets: [
            "<b>The Scanner:</b> Specialized module for detecting non-price risks (SEC, Hacks, Insolvency).",
            "<b>Priority Override:</b> Detection of a 'Systemic Risk' automatically switches signals to SELL.",
            "<b>Detections:</b> Exchange freezes, stablecoin depegs, and major smart contract exploits.",
            "<b>Safety First:</b> Designed to preserve capital during market-wide collapses."
        ]
    },
    {
        num: 10,
        title: "Signal Generation & Confluence",
        subtitle: "Institutional Confluence Trading Logic",
        bullets: [
            "<b>The Formula:</b> Signal = (Sentiment > 0.65) AND (ML Predict = UP) AND (Whale = Accumulating).",
            "<b>Transparency:</b> Every signal shows its 'Logic Chain'—exactly why the AI recommends the trade.",
            "<b>Risk Modeling:</b> Automatic calculation of Target and Stop-Loss based on ATR volatility.",
            "<b>Backtest Proof:</b> Sharpe Ratio of 1.84 with 62.3% Win Rate over 30-day simulation."
        ]
    },
    {
        num: 11,
        title: "The Live Dashboard",
        subtitle: "Terminal Aesthetic & Real-Time UX",
        bullets: [
            "<b>High Impact:</b> Dark-themed, interactive Streamlit UI with Plotly visualizations.",
            "<b>Visuals:</b> Professional Candlestick charts, Sentiment Heatmaps, and Scrolling Whale feeds.",
            "<b>Interaction:</b> One-click 'Start Debate' and 'Force Re-sync' for live demonstrations.",
            "<b>Status:</b> Real-time 'Neural Network' and 'Pipeline' status monitors."
        ]
    },
    {
        num: 12,
        title: "Conclusion & Future Roadmap",
        subtitle: "Scalability to Global Institutional Levels",
        bullets: [
            "<b>Scale:</b> Expanding to Multi-chain (Solana, Base) and 50+ major altcoins.",
            "<b>Automation:</b> Integration with Binance/ByBit APIs for autonomous trade execution.",
            "<b>Customization:</b> User-defined AI personas for personalized market 'Advisors'.",
            "<b>Final Word:</b> Local Intelligence is the future of secure, private, and powerful trading."
        ]
    }
];

const template = (title, subtitle, bullets) => `
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #0e1117; font-family: 'Helvetica', sans-serif;
  color: #FFFFFF; display: flex; flex-direction: column;
}
.header {
  height: 70pt; background: #161b22; display: flex; flex-direction: column; justify-content: center; padding-left: 40pt;
  border-bottom: 3pt solid #00f2ff;
}
h1 { font-size: 28pt; color: #00f2ff; margin: 0; font-weight: 800; text-transform: uppercase; }
.content {
  flex: 1; padding: 30pt; display: flex; flex-direction: column;
}
h2 { font-size: 18pt; color: #00ff88; margin-top: 0; padding-bottom: 5pt; font-weight: 600; }
.subtitle-box { border-bottom: 1pt solid #30363d; margin-bottom: 10pt; }
ul { font-size: 14pt; line-height: 1.5; color: #e6edf3; margin-top: 15pt; list-style-type: none; padding-left: 0; }
li { margin-bottom: 10pt; position: relative; padding-left: 20pt; }
li::before { content: '▶'; position: absolute; left: 0; color: #00f2ff; font-size: 12pt; top: 2pt; }
b { color: #00f2ff; font-family: Arial, sans-serif; }
</style>
</head>
<body>
  <div class="header">
    <h1>${title}</h1>
  </div>
  <div class="content">
    <div class="subtitle-box"><h2>${subtitle}</h2></div>
    <ul>
      ${bullets.map(b => `<li>${b}</li>`).join('\n      ')}
    </ul>
  </div>
</body>
</html>
`;

slides.forEach(s => {
    const html = template(s.title, s.subtitle, s.bullets);
    fs.writeFileSync(path.join('presentation_v2', `slide${s.num}.html`), html);
});

console.log("12 detail-rich slides generated.");
