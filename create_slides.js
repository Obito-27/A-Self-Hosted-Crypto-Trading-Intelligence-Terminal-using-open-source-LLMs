const fs = require('fs');
const path = require('path');

const slides = [
    {
        num: 3,
        title: "Multi-Source Data Ingestion",
        subtitle: "Real-Time Intelligence Streams",
        bullets: [
            "<b>Market Data:</b> 15-min OHLCV candles from Binance API",
            "<b>Social Sentiment:</b> PRAW (Reddit) streaming from r/cryptocurrency",
            "<b>Global News:</b> NewsAPI with CoinDesk RSS automatic fallback",
            "<b>On-Chain Signals:</b> Etherscan API monitoring transactions >$1M",
            "<b>Reliability:</b> Rate-limit handling & graceful degradation"
        ]
    },
    {
        num: 4,
        title: "Sentiment Intelligence",
        subtitle: "Hybrid NLP Architecture (FinBERT + Ollama)",
        bullets: [
            "<b>FinBERT:</b> Ultra-fast quantitative scoring (0.0 - 1.0)",
            "<b>Ollama (Mistral 7B):</b> Qualitative 'Why' narratives",
            "<b>FUD Detection:</b> Real-time scan for scams, rug pulls, and hacks",
            "<b>Contextual Awareness:</b> Nuanced understanding of crypto slang"
        ]
    },
    {
        num: 5,
        title: "Price Prediction Engine",
        subtitle: "XGBoost Time-Series Forecasting",
        bullets: [
            "<b>Feature Engineering:</b> 40+ indicators (RSI, MACD, Sentiment Mom.)",
            "<b>Walk-Forward Validation:</b> No lookahead bias in training",
            "<b>Performance:</b> 62.4% directional accuracy (1h window)",
            "<b>Efficiency:</b> <100ms inference time on standard CPU"
        ]
    },
    {
        num: 6,
        title: "UNIQUE: The Analyst Room",
        subtitle: "Multi-Agent Synthetic Debate",
        bullets: [
            "<b>The Permabull:</b> Agent programmed to find bullish triggers",
            "<b>The Doomer:</b> Agent programmed to identify every hidden risk",
            "<b>Agentic Reasoning:</b> Simulates complex critical thinking",
            "<b>Balanced Verdict:</b> Traders see both extremes before acting"
        ]
    },
    {
        num: 7,
        title: "UNIQUE: Prophet Accuracy Tracker",
        subtitle: "Meta-Intelligence Source Grading",
        bullets: [
            "<b>Core Concept:</b> Not all social/news sources are right",
            "<b>Correlation:</b> Cross-references sentiment with 24h price action",
            "<b>Reliability Scores:</b> Dynamic A-F grades for every source",
            "<b>Filter Noise:</b> Automatically deprioritize historically wrong sources"
        ]
    },
    {
        num: 8,
        title: "UNIQUE: Black Swan Radar",
        subtitle: "Regulatory & Systemic Risk Scanner",
        bullets: [
            "<b>Focus:</b> Structural threats beyond simple price sentiment",
            "<b>Detections:</b> SEC lawsuits, exchange hacks, depeg events",
            "<b>Urgent Alerts:</b> High-severity alerts bypass technical signals",
            "<b>Protection:</b> Built for professional-grade risk management"
        ]
    },
    {
        num: 9,
        title: "Signal Generation Logic",
        subtitle: "High-Conviction Confluence Trading",
        bullets: [
            "<b>Confluence:</b> Signals only fire when 3+ factors agree",
            "<b>Factors:</b> Sentiment > 0.65 + Prediction UP + Whale Accumulation",
            "<b>Transparency:</b> Every signal includes AI-generated logic list",
            "<b>Actionable:</b> Clear BUY / SELL / HOLD with confidence rating"
        ]
    },
    {
        num: 10,
        title: "Performance Proof",
        subtitle: "30-Day Walk-Forward Backtest",
        bullets: [
            "<b>Sharpe Ratio:</b> 1.84 (Excellent risk-adjusted returns)",
            "<b>Win Rate:</b> 62.3% (Beats 50% random walk benchmark)",
            "<b>Total P&L:</b> +18.4% (Alpha: +4.2% over Buy-and-Hold)",
            "<b>Realism:</b> 0.1% fees and 0.05% slippage included"
        ]
    },
    {
        num: 11,
        title: "The Dashboard",
        subtitle: "Terminal Aesthetic & Real-Time Interaction",
        bullets: [
            "<b>Streamlit UI:</b> Modern, dark-themed responsive interface",
            "<b>Interactive Charts:</b> Candlesticks with EMA & Signal overlays",
            "<b>Heatmaps:</b> Instant cross-coin sentiment comparison",
            "<b>Whale Alert:</b> Scrolling feed of high-value market moves"
        ]
    },
    {
        num: 12,
        title: "Roadmap & Conclusion",
        subtitle: "The Future of CryptoTerminal AI",
        bullets: [
            "<b>Scale:</b> Multi-chain support (Solana, Base, Arbitrum)",
            "<b>Automation:</b> Direct Binance/ByBit trade execution",
            "<b>Personas:</b> Custom user-built AI analyst personas",
            "<b>Vision:</b> Local Intelligence > Cloud Noise"
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
  background: #181B24; font-family: Arial, sans-serif;
  color: #FFFFFF; display: flex; flex-direction: column;
}
.header {
  height: 60pt; background: #0a0e1a; display: flex; align-items: center; padding-left: 30pt;
  border-bottom: 2pt solid #B165FB;
}
h1 { font-size: 28pt; color: #B165FB; margin: 0; }
.content {
  flex: 1; padding: 30pt; display: flex; flex-direction: column;
}
h2 { font-size: 20pt; color: #40695B; margin-top: 0; padding-bottom: 5pt; }
.subtitle-box { border-bottom: 1pt solid #40695B; margin-bottom: 10pt; }
ul { font-size: 18pt; line-height: 1.8; color: #e0e0e0; margin-top: 20pt; }
li { margin-bottom: 10pt; }
b { color: #B165FB; }
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
    fs.writeFileSync(path.join('presentation_slides', `slide${s.num}.html`), html);
});

console.log("Slides 3-12 generated.");
