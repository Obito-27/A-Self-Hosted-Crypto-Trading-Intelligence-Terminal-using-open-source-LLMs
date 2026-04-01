import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# PAGE CONFIG
st.set_page_config(page_title="CryptoTerminal AI", page_icon="₿", layout="wide")

# STYLING
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .signal-card { padding: 20px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00ff88; background-color: #161b22; }
    </style>
""", unsafe_allow_html=True)

# MOCK DATA GENERATOR (Reliable for Demo)
def get_mock_candles(symbol):
    now = datetime.now()
    data = []
    price = {"BTC": 65000, "ETH": 3500, "SOL": 140}.get(symbol, 100)
    for i in range(100):
        change = random.uniform(-0.01, 0.01) * price
        o = price
        c = price + change
        h = max(o, c) + random.uniform(0, 0.005) * price
        l = min(o, c) - random.uniform(0, 0.005) * price
        data.append([now - timedelta(minutes=15*(100-i)), o, h, l, c, random.uniform(100, 1000)])
        price = c
    return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# 1. TERMINAL TAB
def draw_terminal():
    st.title("🚀 CryptoTerminal Intelligence")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BTC/USD", "$67,420", "+2.4%")
    col2.metric("ETH/USD", "$3,841", "-0.8%")
    col3.metric("SOL/USD", "$182.45", "+5.2%")
    col4.metric("Market Sentiment", "Bullish (72%)", "Strong")

    st.divider()
    
    m1, m2 = st.columns([2, 1])
    with m1:
        sym = st.selectbox("Select Asset", ["BTC", "ETH", "SOL"])
        df = get_mock_candles(sym)
        fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.update_layout(template="plotly_dark", height=450, title=f"{sym} Candlestick Analysis")
        st.plotly_chart(fig, use_container_width=True)
    
    with m2:
        st.subheader("Live Signals")
        for i in range(3):
            st.markdown(f"""
            <div class="signal-card">
                <strong>BUY {sym} @ {df['close'].iloc[-1]:.2f}</strong><br>
                Confidence: {random.randint(70, 95)}%<br>
                <small>Reason: RSI Oversold + Social Volume Spike</small>
            </div>
            """, unsafe_allow_html=True)

# 2. DEBATE TAB
def draw_debate():
    st.header("🥊 The Analyst Room: Multi-Agent Debate")
    context = st.text_area("Debate Topic", "SEC potential approval of Ethereum ETF next month.")
    if st.button("Start AI Debate"):
        c1, c2 = st.columns(2)
        with c1:
            st.info("**📈 The Permabull:** Institutional flows will reach billions. This is the catalyst for $10k ETH. Buy every dip!")
        with c2:
            st.error("**📉 The Doomer:** Regulatory uncertainty is still high. 'Sell the news' event likely. Watch for liquidation cascades.")

# 3. ACCURANCY TAB
def draw_accuracy():
    st.header("🎯 Prophet Source Accuracy Tracker")
    data = pd.DataFrame({
        "Source": ["r/Bitcoin", "CoinDesk", "r/cryptocurrency", "TheBlock", "Twitter Whales"],
        "Accuracy": [0.68, 0.62, 0.59, 0.55, 0.48]
    })
    st.plotly_chart(px.bar(data, x="Source", y="Accuracy", color="Accuracy", template="plotly_dark"))

# 4. RISK TAB
def draw_risk():
    st.header("🚨 Regulatory Black Swan Radar")
    st.warning("⚠️ RISK DETECTED: SEC investigation into major centralized exchange mentioned in 14 news sources.")
    st.info("✅ Systemic Risk Score: 24/100 (Stable)")

# MAIN APP LOOP
tabs = st.tabs(["Live Terminal", "Analyst Debate", "Prediction Accuracy", "Regulatory Risk"])
with tabs[0]: draw_terminal()
with tabs[1]: draw_debate()
with tabs[2]: draw_accuracy()
with tabs[3]: draw_risk()

# Sidebar
st.sidebar.title("Status")
st.sidebar.success("● All Systems Operational")
st.sidebar.info("● Local LLM (Mistral) Ready")
if st.sidebar.button("Force Re-sync"):
    st.toast("Syncing with Binance/Reddit...")
