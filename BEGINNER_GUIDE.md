# 🎓 Complete Beginner's Guide to MT5-TradeBot API

Welcome! This guide will help you get started with automated trading, even if you're completely new to programming or APIs.

## 📖 What You'll Learn

1. What is an API and why it's useful
2. How to install and set up the project
3. Making your first API call
4. Understanding trading basics
5. Running your first backtest
6. Safety tips for beginners

---

## 🤔 What is an API?

**API** stands for "Application Programming Interface". Think of it as a waiter in a restaurant:
- You (your code) tell the waiter (API) what you want
- The waiter goes to the kitchen (MetaTrader 5)
- The waiter brings back your order (trading data or results)

**Why use an API for trading?**
- Automate repetitive tasks
- Test strategies without manual clicking
- Analyze large amounts of data quickly
- Trade 24/7 without being at your computer

---

## 🛠️ Installation Guide

### Step 1: Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.8 or higher
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"

**Verify installation:**
```bash
python --version
```
You should see: `Python 3.x.x`

### Step 2: Install MetaTrader 5

1. Download MT5 from your broker's website
2. Install and create a demo account
3. Write down your:
   - Login number
   - Password
   - Server name

### Step 3: Download This Project

**Option A - Download ZIP:**
1. Click the green "Code" button on GitHub
2. Click "Download ZIP"
3. Extract to a folder (e.g., `C:\MT5-TradeBot`)

**Option B - Use Git:**
```bash
git clone https://github.com/yourusername/mt5-tradebot-api.git
cd mt5-tradebot-api
```

### Step 4: Install Dependencies

Open Command Prompt in the project folder:
```bash
pip install -r requirements.txt
```

This installs all the libraries the project needs.

### Step 5: Configure Your Credentials

1. Find the file `.env.example`
2. Copy it and rename to `.env`
3. Open `.env` in Notepad
4. Fill in your MT5 details:

```env
MT5_LOGIN=12345678
MT5_PASSWORD=YourPassword123
MT5_SERVER=YourBroker-Demo
```

**Save the file!**

---

## 🚀 Your First API Call

### Start the Server

Open Command Prompt in the project folder:
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Don't close this window!** The server needs to keep running.

### Open the API Documentation

1. Open your web browser
2. Go to: `http://localhost:8001/docs`
3. You'll see a beautiful interactive page!

### Test the Health Check

1. Find `GET /api/v1/health`
2. Click on it to expand
3. Click the blue "Try it out" button
4. Click "Execute"
5. You should see:
```json
{
  "status": "healthy",
  "mt5_connected": false
}
```

**Congratulations!** You just made your first API call! 🎉

### Connect to MT5

1. Find `POST /api/v1/connect`
2. Click "Try it out"
3. You'll see a text box with example data
4. Replace with your credentials:
```json
{
  "login": 12345678,
  "password": "YourPassword123",
  "server": "YourBroker-Demo"
}
```
5. Click "Execute"
6. If successful, you'll see your account info!

---

## 📊 Understanding Trading Basics

### Key Terms

**Symbol:** The trading pair (e.g., EURUSD = Euro vs US Dollar)

**Lot Size:** How much you're trading
- 1.0 lot = $100,000 (standard)
- 0.1 lot = $10,000 (mini)
- 0.01 lot = $1,000 (micro) ← **Start here!**

**Pip:** Smallest price movement (usually 0.0001)

**Stop Loss (SL):** Automatic exit if price goes against you

**Take Profit (TP):** Automatic exit when you reach profit goal

**Leverage:** Borrowed money (1:100 means you can trade $100 with $1)

### Order Types

**BUY (Long):** You think price will go UP
- Buy at 1.1000, sell at 1.1100 = Profit

**SELL (Short):** You think price will go DOWN
- Sell at 1.1000, buy back at 1.0900 = Profit

---

## 🧪 Your First Backtest

Backtesting = Testing a strategy on historical data to see if it would have been profitable.

### Simple Example

1. Open a new Command Prompt window
2. Navigate to the project folder
3. Create a file called `my_first_test.py`:

```python
from ea_tester import EATester
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Connect to MT5
mt5.initialize()

# Create tester
tester = EATester()

# Get 90 days of hourly data for EURUSD
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H1, start_date, end_date)

# Convert to DataFrame
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Apply Moving Average strategy
# When fast MA crosses above slow MA = BUY
# When fast MA crosses below slow MA = SELL
df_strategy = tester.simple_ma_crossover_strategy(df, fast_period=10, slow_period=20)

# Run backtest
results = tester.backtest(
    df_strategy,
    initial_balance=10000.0,  # Start with $10,000
    lot_size=0.1,             # Trade 0.1 lots
    stop_loss_pips=50,        # Exit if lose 50 pips
    take_profit_pips=100      # Exit if gain 100 pips
)

# Print results
print("=" * 50)
print("BACKTEST RESULTS")
print("=" * 50)
print(f"Total Trades: {results['total_trades']}")
print(f"Winning Trades: {results['winning_trades']}")
print(f"Losing Trades: {results['losing_trades']}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Starting Balance: ${results['initial_balance']:.2f}")
print(f"Final Balance: ${results['final_balance']:.2f}")
print(f"Profit/Loss: ${results['final_balance'] - results['initial_balance']:.2f}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
print("=" * 50)

mt5.shutdown()
```

4. Run it:
```bash
python my_first_test.py
```

### Understanding the Results

**Win Rate:** Percentage of profitable trades
- Above 50% is good
- But high win rate doesn't always mean profitable!

**Profit Factor:** Total profit ÷ Total loss
- Above 1.5 is good
- Above 2.0 is excellent

**Max Drawdown:** Largest peak-to-valley loss
- Lower is better
- Shows worst-case scenario

---

## 🛡️ Safety Tips for Beginners

### ⚠️ CRITICAL RULES

1. **ALWAYS use a DEMO account first**
   - Never test on real money
   - Practice for at least 3-6 months

2. **Start with MICRO lots (0.01)**
   - Even on demo, practice good habits
   - Gradually increase as you gain confidence

3. **ALWAYS use Stop Loss**
   - Never trade without protection
   - Risk only 1-2% of account per trade

4. **Don't trust backtests blindly**
   - Past performance ≠ future results
   - Market conditions change

5. **Never trade money you can't afford to lose**
   - Forex is risky
   - Most beginners lose money

### 📋 Pre-Trading Checklist

Before placing any trade:
- [ ] Using demo account?
- [ ] Stop loss set?
- [ ] Position size calculated?
- [ ] Strategy backtested?
- [ ] Understand why you're entering?
- [ ] Know your exit plan?

---

## 🎯 Next Steps

### Week 1: Learn the Basics
- Read about forex trading
- Practice with demo account manually
- Understand how orders work

### Week 2: API Exploration
- Try all API endpoints
- Get comfortable with the documentation
- Make simple API calls

### Week 3: Simple Strategies
- Run provided backtests
- Modify parameters
- Understand what works and why

### Week 4: Create Your Strategy
- Start simple (e.g., MA crossover)
- Backtest thoroughly
- Paper trade (demo) for a month

### Month 2-3: Refine and Learn
- Keep a trading journal
- Analyze what works
- Learn from mistakes
- Study risk management

### Month 4+: Consider Live Trading
- Only if consistently profitable on demo
- Start with smallest possible lots
- Never risk more than 1% per trade

---

## 📚 Learning Resources

### Recommended Reading
- "Trading in the Zone" by Mark Douglas
- "A Random Walk Down Wall Street" by Burton Malkiel
- Investopedia.com for terms and concepts

### Video Tutorials
- Search YouTube for "forex basics"
- Look for risk management tutorials
- Watch strategy explanation videos

### Practice
- Use TradingView for chart analysis
- Join forex forums (be skeptical of "gurus")
- Keep learning and improving

---

## ❓ Common Questions

**Q: How much money do I need to start?**
A: Start with demo (free). For live, minimum $100-500, but practice on demo for months first.

**Q: Can I get rich quick with this?**
A: No. Anyone promising quick riches is lying. Trading takes time, practice, and discipline.

**Q: What's the best strategy?**
A: There's no "best" strategy. What works depends on your style, risk tolerance, and market conditions.

**Q: How long until I'm profitable?**
A: Most traders take 1-2 years to become consistently profitable. Many never do. Be patient.

**Q: Should I use high leverage?**
A: No! High leverage = high risk. Start with low leverage (1:10 or 1:20).

**Q: Can I automate everything?**
A: Yes, but you still need to monitor and adjust. Markets change, strategies need updates.

---

## 🆘 Getting Help

**If something doesn't work:**
1. Check the Troubleshooting section in README.md
2. Read error messages carefully
3. Search Google for the error
4. Ask in the GitHub Issues section
5. Join trading communities (be careful of scams)

**Remember:** Everyone was a beginner once. Don't be afraid to ask questions!

---

## 🎉 Final Words

Trading is a journey, not a destination. Focus on:
- **Learning** over earning
- **Process** over profits
- **Risk management** over returns
- **Consistency** over home runs

Good luck, trade safe, and never stop learning! 🚀

---

**Need help?** Open an issue on GitHub or check the main README.md for more resources.
