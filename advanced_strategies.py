import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class AdvancedStrategies:
    
    @staticmethod
    def bollinger_bands_strategy(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        df['BB_Middle'] = df['close'].rolling(window=period).mean()
        df['BB_Std'] = df['close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * std_dev)
        
        df['Signal'] = 0
        df.loc[df['close'] < df['BB_Lower'], 'Signal'] = 1
        df.loc[df['close'] > df['BB_Upper'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        return df
    
    @staticmethod
    def macd_strategy(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        df['Signal'] = 0
        df.loc[(df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)), 'Signal'] = 1
        df.loc[(df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)), 'Signal'] = -1
        
        df['Position'] = df['Signal']
        return df
    
    @staticmethod
    def stochastic_strategy(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, 
                           oversold: int = 20, overbought: int = 80) -> pd.DataFrame:
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        df['Stoch_K'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()
        
        df['Signal'] = 0
        df.loc[(df['Stoch_K'] < oversold) & (df['Stoch_K'] > df['Stoch_D']), 'Signal'] = 1
        df.loc[(df['Stoch_K'] > overbought) & (df['Stoch_K'] < df['Stoch_D']), 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        return df
    
    @staticmethod
    def ichimoku_strategy(df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, 
                         senkou_b: int = 52) -> pd.DataFrame:
        high_tenkan = df['high'].rolling(window=tenkan).max()
        low_tenkan = df['low'].rolling(window=tenkan).min()
        df['Tenkan_sen'] = (high_tenkan + low_tenkan) / 2
        
        high_kijun = df['high'].rolling(window=kijun).max()
        low_kijun = df['low'].rolling(window=kijun).min()
        df['Kijun_sen'] = (high_kijun + low_kijun) / 2
        
        df['Senkou_span_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(kijun)
        
        high_senkou = df['high'].rolling(window=senkou_b).max()
        low_senkou = df['low'].rolling(window=senkou_b).min()
        df['Senkou_span_B'] = ((high_senkou + low_senkou) / 2).shift(kijun)
        
        df['Chikou_span'] = df['close'].shift(-kijun)
        
        df['Signal'] = 0
        df.loc[(df['Tenkan_sen'] > df['Kijun_sen']) & 
               (df['close'] > df['Senkou_span_A']) & 
               (df['close'] > df['Senkou_span_B']), 'Signal'] = 1
        df.loc[(df['Tenkan_sen'] < df['Kijun_sen']) & 
               (df['close'] < df['Senkou_span_A']) & 
               (df['close'] < df['Senkou_span_B']), 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        return df
    
    @staticmethod
    def atr_trailing_stop(df: pd.DataFrame, period: int = 14, multiplier: float = 2.0) -> pd.DataFrame:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(window=period).mean()
        
        df['Trail_Stop_Long'] = df['close'] - (df['ATR'] * multiplier)
        df['Trail_Stop_Short'] = df['close'] + (df['ATR'] * multiplier)
        
        return df
    
    @staticmethod
    def fibonacci_retracement(df: pd.DataFrame, lookback: int = 50) -> pd.DataFrame:
        rolling_max = df['high'].rolling(window=lookback).max()
        rolling_min = df['low'].rolling(window=lookback).min()
        diff = rolling_max - rolling_min
        
        df['Fib_0'] = rolling_max
        df['Fib_236'] = rolling_max - (diff * 0.236)
        df['Fib_382'] = rolling_max - (diff * 0.382)
        df['Fib_500'] = rolling_max - (diff * 0.500)
        df['Fib_618'] = rolling_max - (diff * 0.618)
        df['Fib_786'] = rolling_max - (diff * 0.786)
        df['Fib_100'] = rolling_min
        
        return df
    
    @staticmethod
    def multi_timeframe_trend(df_h1: pd.DataFrame, df_h4: pd.DataFrame, 
                             df_d1: pd.DataFrame, ma_period: int = 50) -> pd.DataFrame:
        df_h1['MA_H1'] = df_h1['close'].rolling(window=ma_period).mean()
        df_h4['MA_H4'] = df_h4['close'].rolling(window=ma_period).mean()
        df_d1['MA_D1'] = df_d1['close'].rolling(window=ma_period).mean()
        
        df_h1['Trend_H1'] = np.where(df_h1['close'] > df_h1['MA_H1'], 1, -1)
        df_h4['Trend_H4'] = np.where(df_h4['close'] > df_h4['MA_H4'], 1, -1)
        df_d1['Trend_D1'] = np.where(df_d1['close'] > df_d1['MA_D1'], 1, -1)
        
        df_h1 = df_h1.merge(df_h4[['time', 'Trend_H4']], on='time', how='left')
        df_h1 = df_h1.merge(df_d1[['time', 'Trend_D1']], on='time', how='left')
        
        df_h1['Trend_H4'].fillna(method='ffill', inplace=True)
        df_h1['Trend_D1'].fillna(method='ffill', inplace=True)
        
        df_h1['Signal'] = 0
        df_h1.loc[(df_h1['Trend_H1'] == 1) & (df_h1['Trend_H4'] == 1) & (df_h1['Trend_D1'] == 1), 'Signal'] = 1
        df_h1.loc[(df_h1['Trend_H1'] == -1) & (df_h1['Trend_H4'] == -1) & (df_h1['Trend_D1'] == -1), 'Signal'] = -1
        
        df_h1['Position'] = df_h1['Signal'].diff()
        return df_h1
    
    @staticmethod
    def volume_weighted_strategy(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        df['VWAP'] = (df['close'] * df['tick_volume']).rolling(window=period).sum() / df['tick_volume'].rolling(window=period).sum()
        
        df['Volume_MA'] = df['tick_volume'].rolling(window=period).mean()
        df['Volume_Ratio'] = df['tick_volume'] / df['Volume_MA']
        
        df['Signal'] = 0
        df.loc[(df['close'] > df['VWAP']) & (df['Volume_Ratio'] > 1.5), 'Signal'] = 1
        df.loc[(df['close'] < df['VWAP']) & (df['Volume_Ratio'] > 1.5), 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        return df
    
    @staticmethod
    def breakout_strategy(df: pd.DataFrame, lookback: int = 20, volume_threshold: float = 1.5) -> pd.DataFrame:
        df['High_Max'] = df['high'].rolling(window=lookback).max()
        df['Low_Min'] = df['low'].rolling(window=lookback).min()
        
        df['Volume_MA'] = df['tick_volume'].rolling(window=lookback).mean()
        df['Volume_Ratio'] = df['tick_volume'] / df['Volume_MA']
        
        df['Signal'] = 0
        df.loc[(df['close'] > df['High_Max'].shift(1)) & (df['Volume_Ratio'] > volume_threshold), 'Signal'] = 1
        df.loc[(df['close'] < df['Low_Min'].shift(1)) & (df['Volume_Ratio'] > volume_threshold), 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        return df
    
    @staticmethod
    def mean_reversion_strategy(df: pd.DataFrame, period: int = 20, std_threshold: float = 2.0) -> pd.DataFrame:
        df['MA'] = df['close'].rolling(window=period).mean()
        df['Std'] = df['close'].rolling(window=period).std()
        
        df['Z_Score'] = (df['close'] - df['MA']) / df['Std']
        
        df['Signal'] = 0
        df.loc[df['Z_Score'] < -std_threshold, 'Signal'] = 1
        df.loc[df['Z_Score'] > std_threshold, 'Signal'] = -1
        df.loc[abs(df['Z_Score']) < 0.5, 'Signal'] = 0
        
        df['Position'] = df['Signal'].diff()
        return df


class RiskManagement:
    
    @staticmethod
    def calculate_position_size(account_balance: float, risk_percent: float, 
                               stop_loss_pips: float, pip_value: float = 10.0) -> float:
        risk_amount = account_balance * (risk_percent / 100)
        position_size = risk_amount / (stop_loss_pips * pip_value)
        return round(position_size, 2)
    
    @staticmethod
    def calculate_risk_reward_ratio(entry_price: float, stop_loss: float, 
                                   take_profit: float) -> float:
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        return reward / risk if risk > 0 else 0
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        if avg_loss == 0:
            return 0
        win_loss_ratio = avg_win / avg_loss
        kelly_percent = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        return max(0, min(kelly_percent, 0.25))
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Tuple[float, datetime, datetime]:
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max
        max_dd = drawdown.min()
        
        end_idx = drawdown.idxmin()
        start_idx = equity_curve[:end_idx].idxmax()
        
        return abs(max_dd) * 100, start_idx, end_idx
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def trailing_stop_loss(entry_price: float, current_price: float, 
                          atr: float, multiplier: float = 2.0, 
                          position_type: str = 'BUY') -> float:
        if position_type == 'BUY':
            stop_loss = current_price - (atr * multiplier)
            return max(stop_loss, entry_price - (atr * multiplier))
        else:
            stop_loss = current_price + (atr * multiplier)
            return min(stop_loss, entry_price + (atr * multiplier))
