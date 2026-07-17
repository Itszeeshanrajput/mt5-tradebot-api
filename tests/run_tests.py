#!/usr/bin/env python3
"""
Custom Test Runner to execute unit tests without external test frameworks.
Makes testing possible in clean environments where pytest is not installed.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_ea_tester import (
    test_rsi_strategy_mock,
    test_ma_crossover_strategy_mock,
    test_backtest_execution,
    test_backtest_sl_tp,
    test_optimize_parameters_mock
)

def run_test(name, func):
    print(f"Running {name:.<45} ", end="", flush=True)
    try:
        func()
        print("\033[92mPASSED\033[0m")
        return True
    except Exception as e:
        print("\033[91mFAILED\033[0m")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Executing MT5 TradeBot API Unit Tests")
    print("=" * 60)
    
    tests = {
        "test_rsi_strategy_mock": test_rsi_strategy_mock,
        "test_ma_crossover_strategy_mock": test_ma_crossover_strategy_mock,
        "test_backtest_execution": test_backtest_execution,
        "test_backtest_sl_tp": test_backtest_sl_tp,
        "test_optimize_parameters_mock": test_optimize_parameters_mock
    }
    
    success_count = 0
    for name, func in tests.items():
        if run_test(name, func):
            success_count += 1
            
    print("=" * 60)
    print(f"Test Summary: {success_count}/{len(tests)} tests passed")
    print("=" * 60)
    
    if success_count == len(tests):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
