import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

def create_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Create a professional dark-themed candlestick chart."""
    if df.empty:
        return go.Figure()

    # Calculate EMAs if not present
    if 'ema_9' not in df.columns:
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    if 'ema_21' not in df.columns:
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ))

    # EMAs
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ema_9'], name='EMA 9', line=dict(color='white', width=1)))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ema_21'], name='EMA 21', line=dict(color='#ffaa00', width=1)))

    # Layout
    fig.update_layout(
        title=f"{symbol} Price Action",
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0a0e1a",
        xaxis_rangeslider_visible=False,
        yaxis_title="Price (USD)",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(gridcolor="#1a2040", zeroline=False)
    fig.update_yaxes(gridcolor="#1a2040", zeroline=False)

    return fig

def create_sentiment_heatmap(sentiment_data: dict) -> go.Figure:
    """Create a heatmap for sentiment across coins and timeframes."""
    # sentiment_data example: {"BTC": {"1h": 0.78, "4h": 0.72, "24h": 0.65}, ...}
    
    coins = list(sentiment_data.keys())
    timeframes = ["1h", "4h", "24h"]
    
    z_data = []
    for coin in coins:
        row = [sentiment_data[coin].get(tf, 0.5) for tf in timeframes]
        z_data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=timeframes,
        y=coins,
        colorscale='RdYlGn',
        zmin=0, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in z_data],
        texttemplate="%{text}",
        showscale=True
    ))

    fig.update_layout(
        title="Sentiment Heatmap",
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0a0e1a",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300
    )

    return fig
