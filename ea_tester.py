import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EATester:
    def __init__(self):
        self.results = []
        self.trades = []
        self.balance = 0
        self.equity = 0
        
    def calculate_indicators(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        if 'sma_period' in params:
            df['SMA'] = df['close'].rolling(window=params['sma_period']).mean()
        
        if 'ema_period' in params:
            df['EMA'] = df['close'].ewm(span=params['ema_period'], adjust=False).mean()
        
        if 'rsi_period' in params:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_period']).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        
        if 'macd_fast' in params and 'macd_slow' in params and 'macd_signal' in params:
            ema_fast = df['close'].ewm(span=params['macd_fast'], adjust=False).mean()
            ema_slow = df['close'].ewm(span=params['macd_slow'], adjust=False).mean()
            df['MACD'] = ema_fast - ema_slow
            df['MACD_Signal'] = df['MACD'].ewm(span=params['macd_signal'], adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        if 'bb_period' in params and 'bb_std' in params:
            df['BB_Middle'] = df['close'].rolling(window=params['bb_period']).mean()
            df['BB_Std'] = df['close'].rolling(window=params['bb_period']).std()
            df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * params['bb_std'])
            df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * params['bb_std'])
        
        return df
    
    def simple_ma_crossover_strategy(self, df: pd.DataFrame, fast_period: int = 10, slow_period: int = 20) -> pd.DataFrame:
        df['Fast_MA'] = df['close'].rolling(window=fast_period).mean()
        df['Slow_MA'] = df['close'].rolling(window=slow_period).mean()
        
        df['Signal'] = 0
        df.loc[df['Fast_MA'] > df['Slow_MA'], 'Signal'] = 1
        df.loc[df['Fast_MA'] < df['Slow_MA'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def rsi_strategy(self, df: pd.DataFrame, rsi_period: int = 14, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df['Signal'] = 0
        df.loc[df['RSI'] < oversold, 'Signal'] = 1
        df.loc[df['RSI'] > overbought, 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def backtest(self, df: pd.DataFrame, initial_balance: float = 10000.0, 
                 lot_size: float = 0.1, stop_loss_pips: int = 50, 
                 take_profit_pips: int = 100) -> Dict:
        balance = initial_balance
        equity = initial_balance
        trades = []
        open_position = None
        
        for i in range(len(df)):
            if pd.isna(df.iloc[i]['Position']):
                continue
            
            if df.iloc[i]['Position'] == 2:
                if open_position is None:
                    open_position = {
                        'type': 'BUY',
                        'entry_price': df.iloc[i]['close'],
                        'entry_time': df.iloc[i]['time'],
                        'lot_size': lot_size,
                        'sl': df.iloc[i]['close'] - (stop_loss_pips * 0.0001),
                        'tp': df.iloc[i]['close'] + (take_profit_pips * 0.0001)
                    }
            
            elif df.iloc[i]['Position'] == -2:
                if open_position is None:
                    open_position = {
                        'type': 'SELL',
                        'entry_price': df.iloc[i]['close'],
                        'entry_time': df.iloc[i]['time'],
                        'lot_size': lot_size,
                        'sl': df.iloc[i]['close'] + (stop_loss_pips * 0.0001),
                        'tp': df.iloc[i]['close'] - (take_profit_pips * 0.0001)
                    }
            
            if open_position:
                current_price = df.iloc[i]['close']
                
                if open_position['type'] == 'BUY':
                    if current_price <= open_position['sl'] or current_price >= open_position['tp']:
                        exit_price = min(max(current_price, open_position['sl']), open_position['tp'])
                        profit = (exit_price - open_position['entry_price']) * 100000 * lot_size
                        balance += profit
                        
                        trades.append({
                            'type': open_position['type'],
                            'entry_price': open_position['entry_price'],
                            'exit_price': exit_price,
                            'entry_time': open_position['entry_time'],
                            'exit_time': df.iloc[i]['time'],
                            'profit': profit,
                            'balance': balance
                        })
                        open_position = None
                
                elif open_position['type'] == 'SELL':
                    if current_price >= open_position['sl'] or current_price <= open_position['tp']:
                        exit_price = max(min(current_price, open_position['sl']), open_position['tp'])
                        profit = (open_position['entry_price'] - exit_price) * 100000 * lot_size
                        balance += profit
                        
                        trades.append({
                            'type': open_position['type'],
                            'entry_price': open_position['entry_price'],
                            'exit_price': exit_price,
                            'entry_time': open_position['entry_time'],
                            'exit_time': df.iloc[i]['time'],
                            'profit': profit,
                            'balance': balance
                        })
                        open_position = None
        
        if len(trades) == 0:
            return {
                'initial_balance': initial_balance,
                'final_balance': balance,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'total_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'trades': []
            }
        
        trades_df = pd.DataFrame(trades)
        winning_trades = len(trades_df[trades_df['profit'] > 0])
        losing_trades = len(trades_df[trades_df['profit'] < 0])
        total_profit = trades_df[trades_df['profit'] > 0]['profit'].sum() if winning_trades > 0 else 0
        total_loss = abs(trades_df[trades_df['profit'] < 0]['profit'].sum()) if losing_trades > 0 else 0
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        balance_series = trades_df['balance']
        running_max = balance_series.expanding().max()
        drawdown = (balance_series - running_max) / running_max * 100
        max_drawdown = abs(drawdown.min())
        
        return {
            'initial_balance': initial_balance,
            'final_balance': balance,
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / len(trades)) * 100 if len(trades) > 0 else 0,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'trades': trades
        }
    
    def optimize_parameters(self, df: pd.DataFrame, strategy_type: str = 'ma_crossover',
                          param_ranges: Dict = None) -> Dict:
        if param_ranges is None:
            if strategy_type == 'ma_crossover':
                param_ranges = {
                    'fast_period': range(5, 20, 5),
                    'slow_period': range(20, 50, 10)
                }
            elif strategy_type == 'rsi':
                param_ranges = {
                    'rsi_period': range(10, 20, 2),
                    'oversold': range(20, 35, 5),
                    'overbought': range(65, 80, 5)
                }
        
        best_result = None
        best_params = None
        best_profit = float('-inf')
        
        if strategy_type == 'ma_crossover':
            for fast in param_ranges['fast_period']:
                for slow in param_ranges['slow_period']:
                    if fast >= slow:
                        continue
                    
                    test_df = df.copy()
                    test_df = self.simple_ma_crossover_strategy(test_df, fast, slow)
                    result = self.backtest(test_df)
                    
                    if result['final_balance'] > best_profit:
                        best_profit = result['final_balance']
                        best_result = result
                        best_params = {'fast_period': fast, 'slow_period': slow}
        
        elif strategy_type == 'rsi':
            for period in param_ranges['rsi_period']:
                for oversold in param_ranges['oversold']:
                    for overbought in param_ranges['overbought']:
                        test_df = df.copy()
                        test_df = self.rsi_strategy(test_df, period, oversold, overbought)
                        result = self.backtest(test_df)
                        
                        if result['final_balance'] > best_profit:
                            best_profit = result['final_balance']
                            best_result = result
                            best_params = {
                                'rsi_period': period,
                                'oversold': oversold,
                                'overbought': overbought
                            }
        
        return {
            'best_params': best_params,
            'best_result': best_result
        }
