import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ea_tester import EATester

def create_mock_data(bars=100, trend='up'):
    """Helper to create mock OHLCV dataframe"""
    start_time = datetime.now() - timedelta(hours=bars)
    times = [start_time + timedelta(hours=i) for i in range(bars)]
    
    np.random.seed(42)
    # Generate prices
    if trend == 'up':
        closes = 1.1000 + np.cumsum(np.random.normal(0.0005, 0.001, bars))
    elif trend == 'down':
        closes = 1.1000 + np.cumsum(np.random.normal(-0.0005, 0.001, bars))
    else: # Sideways
        closes = 1.1000 + np.cumsum(np.random.normal(0, 0.001, bars))
        
    highs = closes + np.random.uniform(0.0002, 0.0008, bars)
    lows = closes - np.random.uniform(0.0002, 0.0008, bars)
    opens = np.roll(closes, 1)
    opens[0] = closes[0]
    volumes = np.random.randint(100, 1000, bars)
    
    df = pd.DataFrame({
        'time': times,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'tick_volume': volumes
    })
    return df

def test_rsi_strategy_mock():
    tester = EATester()
    df = create_mock_data(bars=50, trend='sideways')
    
    # Run strategy
    df_rsi = tester.run_strategy(df, 'rsi', {'rsi_period': 14, 'oversold': 30, 'overbought': 70})
    
    assert 'signal' in df_rsi.columns
    assert 'RSI' in df_rsi.columns

def test_ma_crossover_strategy_mock():
    tester = EATester()
    df = create_mock_data(bars=50, trend='up')
    
    df_ma = tester.run_strategy(df, 'simple_ma_crossover', {'fast_period': 5, 'slow_period': 15})
    
    assert 'signal' in df_ma.columns
    assert 'Fast_MA' in df_ma.columns
    assert 'Slow_MA' in df_ma.columns

def test_backtest_execution():
    tester = EATester()
    df = create_mock_data(bars=100, trend='sideways')
    
    # Manually inject signals to test trade transitions and exits
    # We want to test transitions from flat (0) to buy (1), buy (1) to sell (-1), etc.
    df['signal'] = 0
    df.loc[10, 'signal'] = 1   # Entry BUY
    df.loc[30, 'signal'] = -1  # Exit BUY & Entry SELL
    df.loc[60, 'signal'] = 0   # Exit SELL
    
    results = tester.backtest(df, initial_balance=10000.0, lot_size=0.1, stop_loss_pips=0, take_profit_pips=0)
    
    # There should be 2 completed trades:
    # 1. Long entered at index 10, exited at index 30 (reason: opposite signal)
    # 2. Short entered at index 30, exited at index 60 (reason: neutral signal)
    assert results['total_trades'] == 2
    assert len(results['trades']) == 2
    assert results['trades'][0]['type'] == 'BUY'
    assert results['trades'][0]['reason'] == 'Signal'
    assert results['trades'][1]['type'] == 'SELL'
    assert results['trades'][1]['reason'] == 'Signal'
    
    # Balance should be updated
    assert results['final_balance'] != 10000.0
    assert len(results['equity_curve']) == len(df)
    assert len(results['timestamps']) == len(df)

def test_backtest_sl_tp():
    tester = EATester()
    df = create_mock_data(bars=50, trend='up')
    
    # Manually set price spike to hit SL/TP
    # Let's say entry price at index 5 is 1.1000.
    # High at index 6 is 1.2000, which will hit TP of 100 pips (0.0100) easily.
    df.loc[5, 'close'] = 1.1000
    df.loc[5, 'signal'] = 1  # Enter BUY
    
    df.loc[6, 'open'] = 1.1000
    df.loc[6, 'low'] = 1.0900
    df.loc[6, 'high'] = 1.2000 # Spikes high
    df.loc[6, 'close'] = 1.1500
    
    # Run backtest with 50 pips TP (0.0050) and 200 pips SL
    results = tester.backtest(df, initial_balance=10000.0, lot_size=0.1, stop_loss_pips=200, take_profit_pips=50)
    
    assert results['total_trades'] == 1
    assert results['trades'][0]['reason'] == 'TP'
    assert results['trades'][0]['exit_price'] == 1.1050 # Entry 1.1000 + 50 pips

def test_optimize_parameters_mock():
    tester = EATester()
    df = create_mock_data(bars=50, trend='up')
    
    param_ranges = {
        'fast_period': [5, 8],
        'slow_period': [15, 20]
    }
    
    opt_res = tester.optimize_parameters(df, 'simple_ma_crossover', param_ranges)
    
    assert 'best_params' in opt_res
    assert 'best_result' in opt_res
    assert 'fast_period' in opt_res['best_params']
    assert 'slow_period' in opt_res['best_params']
