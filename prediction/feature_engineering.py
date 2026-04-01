import pandas as pd
import numpy as np
from ta import momentum, trend, volatility, volume as ta_volume

class FeatureEngineer:
    
    def build_features(self, price_df: pd.DataFrame, sentiment_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Build complete feature matrix from OHLCV + sentiment data.
        """
        if price_df.empty:
            return pd.DataFrame()
            
        df = price_df.copy()
        df = df.sort_values('timestamp')
        
        # 1. Add Technical Indicators
        df = self.add_price_features(df)
        
        # 2. Add Time Features
        df = self.add_time_features(df)
        
        # 3. Add Sentiment Features if available
        if sentiment_df is not None and not sentiment_df.empty:
            df = self.add_sentiment_features(df, sentiment_df)
        
        # 4. Fill NaNs from technical indicators
        df = df.ffill().fillna(0)
        
        return df

    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum, trend, volatility, and volume indicators."""
        # Momentum
        df['rsi'] = momentum.RSIIndicator(df['close']).rsi()
        stoch = momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        df['roc_5'] = momentum.ROCIndicator(df['close'], window=5).roc()
        df['roc_15'] = momentum.ROCIndicator(df['close'], window=15).roc()
        df['william_r'] = momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
        
        # Trend
        df['ema_9_ratio'] = trend.EMAIndicator(df['close'], window=9).ema_indicator() / df['close']
        df['ema_21_ratio'] = trend.EMAIndicator(df['close'], window=21).ema_indicator() / df['close']
        df['ema_50_ratio'] = trend.EMAIndicator(df['close'], window=50).ema_indicator() / df['close']
        
        macd = trend.MACD(df['close'])
        df['macd_line'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()
        df['adx'] = trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
        
        # Volatility
        bb = volatility.BollingerBands(df['close'])
        df['bb_width'] = (bb.bollinger_hband() - bb.bollinger_lband()) / df['close']
        df['bb_pos'] = (df['close'] - bb.bollinger_lband()) / (bb.bollinger_hband() - bb.bollinger_lband())
        df['atr_ratio'] = volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range() / df['close']
        df['hist_vol'] = df['close'].pct_change().rolling(window=20).std()
        
        # Volume
        df['vol_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        obv = ta_volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
        df['obv_momentum'] = obv / obv.shift(10)
        
        # Price Patterns
        for h in [1, 4, 12, 24, 48]:
            df[f'return_{h}h'] = df['close'].pct_change(periods=h*4) # 15min * 4 = 1h
            
        df['price_pos_24h'] = (df['close'] - df['low'].rolling(96).min()) / (df['high'].rolling(96).max() - df['low'].rolling(96).min())
        df['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        
        return df

    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add cyclical time features."""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_asian_session'] = df['hour'].between(0, 8).astype(int)
        df['is_us_session'] = df['hour'].between(13, 21).astype(int)
        
        return df

    def add_sentiment_features(self, df: pd.DataFrame, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """Merge and process sentiment data."""
        sentiment_df['timestamp'] = pd.to_datetime(sentiment_df['created_at']).dt.floor('15T')
        
        # Aggregate sentiment by 15min intervals
        agg_sent = sentiment_df.groupby('timestamp').agg(
            avg_score=('sentiment_score', 'mean'),
            post_count=('id', 'count')
        ).reset_index()
        
        # Merge with price data
        df = pd.merge_asof(df.sort_values('timestamp'), agg_sent.sort_values('timestamp'), on='timestamp', direction='backward')
        
        # Rolling sentiment
        df['sentiment_1h'] = df['avg_score'].rolling(4).mean()
        df['sentiment_4h'] = df['avg_score'].rolling(16).mean()
        df['sentiment_24h'] = df['avg_score'].rolling(96).mean()
        df['sentiment_momentum'] = df['sentiment_1h'] - df['sentiment_24h']
        df['sentiment_volume'] = df['post_count'].rolling(4).sum()
        
        return df

    def build_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target labels for training."""
        timeframes = {"1h": 4, "4h": 16, "24h": 96}
        threshold = 0.005 # 0.5%
        
        for name, candles in timeframes.items():
            future_return = (df['close'].shift(-candles) - df['close']) / df['close']
            
            conditions = [
                (future_return > threshold),
                (future_return < -threshold)
            ]
            choices = ['UP', 'DOWN']
            df[f'target_{name}'] = np.select(conditions, choices, default='SIDEWAYS')
            
            # Mask the rows where we don't have future data
            df.loc[df.index[-candles:], f'target_{name}'] = np.nan
            
        return df
