try:
    import MetaTrader5 as mt5
except ImportError:
    # MetaTrader5 is Windows-only. We stub it here to allow offline development/tests on Linux.
    class MetaTrader5Mock:
        TIMEFRAME_M1 = 1
        TIMEFRAME_M5 = 5
        TIMEFRAME_M15 = 15
        TIMEFRAME_M30 = 30
        TIMEFRAME_H1 = 16385
        TIMEFRAME_H4 = 16388
        TIMEFRAME_D1 = 16408
        TIMEFRAME_W1 = 32769
        TIMEFRAME_MN1 = 49153
        
        ORDER_TYPE_BUY = 0
        ORDER_TYPE_SELL = 1
        ORDER_TYPE_BUY_LIMIT = 2
        ORDER_TYPE_SELL_LIMIT = 3
        ORDER_TYPE_BUY_STOP = 4
        ORDER_TYPE_SELL_STOP = 5
        
        TRADE_ACTION_DEAL = 1
        ORDER_TIME_GTC = 0
        ORDER_FILLING_IOC = 1
        TRADE_RETCODE_DONE = 10009
        
        POSITION_TYPE_BUY = 0
        POSITION_TYPE_SELL = 1

        def initialize(self, *args, **kwargs):
            return False
            
        def shutdown(self):
            pass
            
        def last_error(self):
            return (1, "MetaTrader5 is not supported on Linux")
            
        def account_info(self):
            return None
            
        def positions_get(self, *args, **kwargs):
            return None
            
        def orders_get(self, *args, **kwargs):
            return None
            
        def symbol_info(self, *args, **kwargs):
            return None
            
        def symbol_info_tick(self, *args, **kwargs):
            return None
            
        def symbol_select(self, *args, **kwargs):
            return False
            
        def symbols_get(self, *args, **kwargs):
            return None
            
        def order_send(self, *args, **kwargs):
            class DummyResult:
                retcode = 1
                comment = "MT5 not supported on Linux"
                order = 0
                def _asdict(self):
                    return {}
            return DummyResult()
            
        def copy_rates_range(self, *args, **kwargs):
            return None
            
        def copy_rates_from_pos(self, *args, **kwargs):
            return None
            
        def history_deals_get(self, *args, **kwargs):
            return None

    mt5 = MetaTrader5Mock()
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class EATester:
    def __init__(self):
        self.results = []
        self.trades = []
        self.balance = 0
        self.equity = 0
        
    def calculate_indicators(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        df = df.copy()
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
        df = df.copy()
        df['Fast_MA'] = df['close'].rolling(window=fast_period).mean()
        df['Slow_MA'] = df['close'].rolling(window=slow_period).mean()
        
        df['signal'] = 0
        df.loc[df['Fast_MA'] > df['Slow_MA'], 'signal'] = 1
        df.loc[df['Fast_MA'] < df['Slow_MA'], 'signal'] = -1
        return df
    
    def rsi_strategy(self, df: pd.DataFrame, rsi_period: int = 14, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
        df = df.copy()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df['signal'] = 0
        df.loc[df['RSI'] < oversold, 'signal'] = 1
        df.loc[df['RSI'] > overbought, 'signal'] = -1
        return df
    
    def run_strategy(self, df: pd.DataFrame, strategy_name: str, strategy_params: Dict) -> pd.DataFrame:
        from advanced_strategies import AdvancedStrategies
        
        # Make a copy and normalize columns to lowercase
        df_copy = df.copy()
        df_copy.columns = [c.lower() for c in df_copy.columns]
        
        if strategy_name == 'bollinger_bands':
            period = int(strategy_params.get('period', 20))
            std_dev = float(strategy_params.get('std_dev', 2.0))
            res = AdvancedStrategies.bollinger_bands_strategy(df_copy, period, std_dev)
        elif strategy_name == 'macd':
            fast = int(strategy_params.get('fast', 12))
            slow = int(strategy_params.get('slow', 26))
            signal = int(strategy_params.get('signal', 9))
            res = AdvancedStrategies.macd_strategy(df_copy, fast, slow, signal)
        elif strategy_name == 'stochastic':
            k_period = int(strategy_params.get('k_period', 14))
            d_period = int(strategy_params.get('d_period', 3))
            oversold = int(strategy_params.get('oversold', 20))
            overbought = int(strategy_params.get('overbought', 80))
            res = AdvancedStrategies.stochastic_strategy(df_copy, k_period, d_period, oversold, overbought)
        elif strategy_name == 'ichimoku':
            tenkan = int(strategy_params.get('tenkan', 9))
            kijun = int(strategy_params.get('kijun', 26))
            senkou_b = int(strategy_params.get('senkou_b', 52))
            res = AdvancedStrategies.ichimoku_strategy(df_copy, tenkan, kijun, senkou_b)
        elif strategy_name == 'vwap':
            period = int(strategy_params.get('period', 20))
            res = AdvancedStrategies.volume_weighted_strategy(df_copy, period)
        elif strategy_name == 'breakout':
            lookback = int(strategy_params.get('lookback', 20))
            volume_threshold = float(strategy_params.get('volume_threshold', 1.5))
            res = AdvancedStrategies.breakout_strategy(df_copy, lookback, volume_threshold)
        elif strategy_name == 'mean_reversion':
            period = int(strategy_params.get('period', 20))
            std_threshold = float(strategy_params.get('std_threshold', 2.0))
            res = AdvancedStrategies.mean_reversion_strategy(df_copy, period, std_threshold)
        elif strategy_name == 'simple_ma_crossover':
            fast = int(strategy_params.get('fast_period', 10))
            slow = int(strategy_params.get('slow_period', 20))
            res = self.simple_ma_crossover_strategy(df_copy, fast, slow)
        elif strategy_name == 'rsi':
            rsi_period = int(strategy_params.get('rsi_period', 14))
            oversold = int(strategy_params.get('oversold', 30))
            overbought = int(strategy_params.get('overbought', 70))
            res = self.rsi_strategy(df_copy, rsi_period, oversold, overbought)
        else:
            raise ValueError(f"Unknown strategy name: {strategy_name}")
            
        # Ensure 'signal' column is in lowercase
        if 'Signal' in res.columns and 'signal' not in res.columns:
            res['signal'] = res['Signal']
        return res
        
    def backtest(self, df: pd.DataFrame, initial_balance: float = 10000.0, 
                 lot_size: float = 0.1, stop_loss_pips: float = 0.0, 
                 take_profit_pips: float = 0.0, exit_on_opposite_signal: bool = True) -> Dict[str, Any]:
        balance = initial_balance
        trades = []
        open_position = None
        
        # Ensure column names are lowercase
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        
        # Default signal handling (fill na with 0)
        if 'signal' not in df.columns:
            df['signal'] = 0
        df['signal'] = df['signal'].fillna(0).astype(int)
        
        equity_curve = []
        timestamps = []
        
        # Multiplier depending on symbol
        pip_size = 0.0001
        contract_size = 100000.0
        
        # Simple heuristic to identify currency scale (e.g. JPY, Gold, Cryptos)
        if len(df) > 0:
            first_close = df.iloc[0]['close']
            if first_close > 1000:  # Gold, BTC, etc.
                pip_size = 0.1
                contract_size = 100.0  # Gold standard contract
            elif first_close > 50:  # USDJPY, etc.
                pip_size = 0.01
                contract_size = 1000.0
                
        for i in range(len(df)):
            row = df.iloc[i]
            current_price = row['close']
            current_high = row.get('high', current_price)
            current_low = row.get('low', current_price)
            current_time = row['time']
            
            # Check open position first
            if open_position:
                pos_type = open_position['type']
                entry_price = open_position['entry_price']
                sl = open_position['sl']
                tp = open_position['tp']
                
                closed = False
                exit_price = current_price
                exit_reason = "Signal"
                
                if pos_type == 'BUY':
                    if sl and current_low <= sl:
                        exit_price = sl
                        exit_reason = "SL"
                        closed = True
                    elif tp and current_high >= tp:
                        exit_price = tp
                        exit_reason = "TP"
                        closed = True
                    elif exit_on_opposite_signal and (row['signal'] == -1 or row['signal'] == 0):
                        exit_price = current_price
                        exit_reason = "Signal"
                        closed = True
                
                elif pos_type == 'SELL':
                    if sl and current_high >= sl:
                        exit_price = sl
                        exit_reason = "SL"
                        closed = True
                    elif tp and current_low <= tp:
                        exit_price = tp
                        exit_reason = "TP"
                        closed = True
                    elif exit_on_opposite_signal and (row['signal'] == 1 or row['signal'] == 0):
                        exit_price = current_price
                        exit_reason = "Signal"
                        closed = True
                
                if closed:
                    if pos_type == 'BUY':
                        profit = (exit_price - entry_price) * contract_size * lot_size
                    else:
                        profit = (entry_price - exit_price) * contract_size * lot_size
                        
                    balance += profit
                    trades.append({
                        'type': pos_type,
                        'entry_price': float(entry_price),
                        'exit_price': float(exit_price),
                        'entry_time': str(open_position['entry_time']),
                        'exit_time': str(current_time),
                        'profit': float(profit),
                        'balance': float(balance),
                        'reason': exit_reason
                    })
                    open_position = None
            
            # Open position if signal changed and we have no active position
            if not open_position and i > 0:
                prev_signal = df.iloc[i-1]['signal']
                curr_signal = row['signal']
                
                # Check for new active signal
                if curr_signal == 1 and prev_signal != 1:
                    sl = current_price - (stop_loss_pips * pip_size) if stop_loss_pips > 0 else None
                    tp = current_price + (take_profit_pips * pip_size) if take_profit_pips > 0 else None
                    open_position = {
                        'type': 'BUY',
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'lot_size': lot_size,
                        'sl': sl,
                        'tp': tp
                    }
                elif curr_signal == -1 and prev_signal != -1:
                    sl = current_price + (stop_loss_pips * pip_size) if stop_loss_pips > 0 else None
                    tp = current_price - (take_profit_pips * pip_size) if take_profit_pips > 0 else None
                    open_position = {
                        'type': 'SELL',
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'lot_size': lot_size,
                        'sl': sl,
                        'tp': tp
                    }
            
            # Track equity curve
            current_equity = balance
            if open_position:
                pos_type = open_position['type']
                entry_price = open_position['entry_price']
                if pos_type == 'BUY':
                    current_equity += (current_price - entry_price) * contract_size * lot_size
                else:
                    current_equity += (entry_price - current_price) * contract_size * lot_size
            
            equity_curve.append(float(current_equity))
            if isinstance(current_time, datetime):
                timestamps.append(current_time.isoformat())
            else:
                timestamps.append(str(current_time))
                
        # Calculate final stats
        if len(trades) == 0:
            return {
                'initial_balance': float(initial_balance),
                'final_balance': float(balance),
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'total_loss': 0.0,
                'profit_factor': 0.0,
                'max_drawdown': 0.0,
                'trades': [],
                'equity_curve': equity_curve,
                'timestamps': timestamps
            }
            
        trades_df = pd.DataFrame(trades)
        winning_trades = int(len(trades_df[trades_df['profit'] > 0]))
        losing_trades = int(len(trades_df[trades_df['profit'] < 0]))
        total_profit = float(trades_df[trades_df['profit'] > 0]['profit'].sum() if winning_trades > 0 else 0)
        total_loss = float(abs(trades_df[trades_df['profit'] < 0]['profit'].sum()) if losing_trades > 0 else 0)
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        if profit_factor == float('inf'):
            profit_factor = 99.9  # Clean representation for JSON
            
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = float(abs(drawdown.min())) if not drawdown.empty else 0.0
        
        return {
            'initial_balance': float(initial_balance),
            'final_balance': float(balance),
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': float((winning_trades / len(trades)) * 100),
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'trades': trades,
            'equity_curve': equity_curve,
            'timestamps': timestamps
        }
    
    def optimize_parameters(self, df: pd.DataFrame, strategy_name: str,
                           param_ranges: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimizes a strategy's parameters over a given DataFrame.
        param_ranges expects keys matching the strategy's parameters with a list of values to search.
        """
        import itertools
        
        keys, values = zip(*param_ranges.items())
        permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        best_result = None
        best_params = None
        best_profit = float('-inf')
        
        for params in permutations:
            try:
                test_df = self.run_strategy(df, strategy_name, params)
                result = self.backtest(test_df)
                
                if result['final_balance'] > best_profit:
                    best_profit = result['final_balance']
                    best_result = result
                    best_params = params
            except Exception as e:
                logger.error(f"Error evaluating params {params} for {strategy_name}: {e}")
                
        return {
            'best_params': best_params,
            'best_result': best_result
        }
