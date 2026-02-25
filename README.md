# 🚀 MT5-TradeBot API

**Professional RESTful API for MetaTrader 5 Expert Advisor Testing & Automation**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MT5](https://img.shields.io/badge/MetaTrader-5-orange.svg)](https://www.metatrader5.com/)

> A powerful, easy-to-use API for testing trading strategies, backtesting Expert Advisors, and automating forex trading operations via MetaTrader 5.

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Beginner's Guide](#-beginners-guide)
- [API Documentation](#-api-documentation)
- [Examples](#-examples)
- [Backtesting](#-backtesting)
- [Trading Strategies](#-trading-strategies)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Capabilities
- ✅ **Full MT5 Integration** - Connect to any MetaTrader 5 broker
- ✅ **RESTful API** - Easy integration with any programming language
- ✅ **Real-time Data** - Live market prices, account info, and positions
- ✅ **Order Management** - Place, modify, and close trades programmatically
- ✅ **Historical Data** - Access OHLCV data for any symbol and timeframe
- ✅ **Backtesting Engine** - Test strategies with historical data
- ✅ **10+ Built-in Strategies** - MA, RSI, MACD, Bollinger Bands, and more
- ✅ **Risk Management** - Kelly Criterion, Sharpe Ratio, VaR calculations
- ✅ **Auto-Documentation** - Interactive Swagger UI included

### Perfect For
- 🎯 Beginner traders learning algorithmic trading
- 📊 Strategy developers testing Expert Advisors
- 🤖 Automation enthusiasts building trading bots
- 📈 Quantitative analysts backtesting strategies
- 💼 Professional traders optimizing parameters

---

## 🚀 Quick Start

### Prerequisites
- Windows OS (MT5 requirement)
- Python 3.8 or higher
- MetaTrader 5 installed
- MT5 trading account (demo or live)

### Installation (3 Steps)

**Step 1: Clone the repository**
```bash
git clone https://github.com/yourusername/mt5-tradebot-api.git
cd mt5-tradebot-api
```

**Step 2: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Configure your MT5 credentials**
```bash
copy .env.example .env
```

Edit `.env` file:
```env
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

### Run the API

**Option A - Python:**
```bash
python main.py
```

**Option B - Batch File (Windows):**
```bash
start_api.bat
```

**Access the API:**
- API Server: http://localhost:8001
- Interactive Docs: http://localhost:8001/docs
- Alternative Docs: http://localhost:8001/redoc

---

## 📚 Beginner's Guide

### What is This Project?

MT5-TradeBot API is a bridge between your code and MetaTrader 5. It lets you:
- Check your account balance
- Get live market prices
- Place buy/sell orders
- Test trading strategies
- Analyze historical data

All through simple HTTP requests (like visiting a website)!

### Your First API Call

**1. Start the server** (see Quick Start above)

**2. Open your browser** and go to: http://localhost:8001/docs

**3. Try the "Health Check" endpoint:**
- Click on `GET /api/v1/health`
- Click "Try it out"
- Click "Execute"
- You'll see: `{"status": "healthy"}`

**4. Connect to MT5:**
- Find `POST /api/v1/connect`
- Click "Try it out"
- Fill in your credentials:
```json
{
  "login": 12345678,
  "password": "your_password",
  "server": "YourBroker-Server"
}
```
- Click "Execute"
- Success! You're connected!

### Understanding the Response

When you make a request, you get JSON back:
```json
{
  "status": "success",
  "data": {
    "balance": 10000.00,
    "equity": 10000.00
  }
}
```

- `status`: "success" or "error"
- `data`: The information you requested

---

## 📖 API Documentation

### Connection Endpoints

#### Connect to MT5
```http
POST /api/v1/connect
```
**Request:**
```json
{
  "login": 262323581,
  "password": "your_password",
  "server": "Exness-MT5Trial16"
}
```

#### Disconnect
```http
POST /api/v1/disconnect
```

### Account Endpoints

#### Get Account Info
```http
GET /api/v1/account
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "login": 262323581,
    "balance": 118.40,
    "equity": 118.40,
    "leverage": 2000,
    "currency": "USD"
  }
}
```

### Trading Endpoints

#### Get Open Positions
```http
GET /api/v1/positions
```

#### Place Order
```http
POST /api/v1/order/place
```
**Request:**
```json
{
  "symbol": "EURUSD",
  "order_type": "BUY",
  "volume": 0.01,
  "sl": 1.0500,
  "tp": 1.0700
}
```

#### Close Position
```http
POST /api/v1/position/close/{position_id}
```

### Market Data Endpoints

#### Get Symbols
```http
GET /api/v1/symbols
```

#### Get Current Tick
```http
GET /api/v1/symbol/{symbol}/tick
```

#### Get Historical Data
```http
POST /api/v1/historical-data
```
**Request:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59"
}
```

**Supported Timeframes:**
- `M1`, `M5`, `M15`, `M30` (Minutes)
- `H1`, `H4` (Hours)
- `D1` (Daily)
- `W1` (Weekly)
- `MN1` (Monthly)

---

## 💡 Examples

### Python Example

```python
from test_client import MT5APIClient
from datetime import datetime, timedelta

# Initialize client
client = MT5APIClient("http://localhost:8001/api/v1")

# Connect to MT5
client.connect(
    login=262323581,
    password="your_password",
    server="Exness-MT5Trial16"
)

# Get account balance
account = client.get_account_info()
print(f"Balance: ${account['data']['balance']:.2f}")

# Get current price
tick = client.get_symbol_tick("EURUSD")
print(f"EURUSD: {tick['data']['bid']:.5f}")

# Get historical data
end = datetime.now()
start = end - timedelta(days=7)
data = client.get_historical_data("EURUSD", "H1", start, end)
print(f"Retrieved {data['bars_count']} bars")

# Place a trade (demo account recommended!)
order = client.place_order(
    symbol="EURUSD",
    order_type="BUY",
    volume=0.01,
    sl=1.0500,
    tp=1.0700
)
print(f"Order placed: {order}")
```

### cURL Example

```bash
# Connect to MT5
curl -X POST "http://localhost:8001/api/v1/connect" \
  -H "Content-Type: application/json" \
  -d '{
    "login": 262323581,
    "password": "your_password",
    "server": "Exness-MT5Trial16"
  }'

# Get account info
curl http://localhost:8001/api/v1/account

# Get current price
curl http://localhost:8001/api/v1/symbol/EURUSD/tick
```

### JavaScript Example

```javascript
// Connect to MT5
const response = await fetch('http://localhost:8001/api/v1/connect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    login: 262323581,
    password: 'your_password',
    server: 'Exness-MT5Trial16'
  })
});

const result = await response.json();
console.log('Connected:', result);

// Get account info
const account = await fetch('http://localhost:8001/api/v1/account');
const accountData = await account.json();
console.log('Balance:', accountData.data.balance);
```

---

## 🧪 Backtesting

Test your trading strategies with historical data before risking real money!

### Simple Moving Average Strategy

```python
from ea_tester import EATester
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialize
mt5.initialize()
tester = EATester()

# Get historical data
end = datetime.now()
start = end - timedelta(days=90)
rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H1, start, end)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Apply strategy
df_strategy = tester.simple_ma_crossover_strategy(
    df, 
    fast_period=10, 
    slow_period=20
)

# Run backtest
results = tester.backtest(
    df_strategy,
    initial_balance=10000.0,
    lot_size=0.1,
    stop_loss_pips=50,
    take_profit_pips=100
)

# Print results
print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Final Balance: ${results['final_balance']:.2f}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

### Optimize Strategy Parameters

```python
# Find the best parameters
optimization = tester.optimize_parameters(
    df, 
    strategy_type='ma_crossover',
    param_ranges={
        'fast_period': range(5, 20, 5),
        'slow_period': range(20, 50, 10)
    }
)

print(f"Best Parameters: {optimization['best_params']}")
print(f"Best Profit: ${optimization['best_result']['final_balance']:.2f}")
```

---

## 📊 Trading Strategies

### Built-in Strategies

1. **Moving Average Crossover**
   - Fast MA crosses above/below Slow MA
   - Classic trend-following strategy

2. **RSI Strategy**
   - Oversold/overbought levels
   - Mean reversion approach

3. **Bollinger Bands**
   - Price touches upper/lower bands
   - Volatility-based trading

4. **MACD**
   - MACD line crosses signal line
   - Momentum strategy

5. **Stochastic Oscillator**
   - K/D line crossovers
   - Overbought/oversold conditions

6. **Ichimoku Cloud**
   - Multi-indicator system
   - Trend and support/resistance

7. **Breakout Strategy**
   - Price breaks range highs/lows
   - Volume confirmation

8. **Mean Reversion**
   - Z-score based entries
   - Statistical approach

9. **Volume Weighted**
   - VWAP-based signals
   - Institutional levels

10. **Multi-Timeframe**
    - Trend alignment across timeframes
    - Higher probability setups

### Using Advanced Strategies

```python
from advanced_strategies import AdvancedStrategies
import pandas as pd

# Load your data
df = pd.DataFrame(...)  # Your OHLCV data

# Apply Bollinger Bands strategy
strategy = AdvancedStrategies()
df_bb = strategy.bollinger_bands_strategy(df, period=20, std_dev=2.0)

# Apply MACD strategy
df_macd = strategy.macd_strategy(df, fast=12, slow=26, signal=9)

# Apply Ichimoku strategy
df_ichimoku = strategy.ichimoku_strategy(df)
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# MT5 Connection
MT5_LOGIN=262323581
MT5_PASSWORD=your_password
MT5_SERVER=Exness-MT5Trial16
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
LOG_LEVEL=INFO
```

### Custom Configuration

Edit `config.py` for advanced settings:

```python
class Settings(BaseSettings):
    API_TITLE: str = "MT5-TradeBot API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    
    # Add your custom settings here
```

---

## 🔧 Troubleshooting

### Common Issues

**1. "MT5 initialization failed"**
- ✅ Ensure MetaTrader 5 is installed
- ✅ Check credentials in `.env` file
- ✅ Verify MT5 terminal is running
- ✅ Enable "Allow DLL imports" in MT5 settings

**2. "Port already in use"**
- Change port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8002)
```

**3. "Symbol not found"**
- Use `GET /api/v1/symbols` to see available symbols
- Different brokers have different symbol names
- Try "EURUSD", "EURUSDm", or "EURUSD.m"

**4. "No historical data"**
- Some symbols may not have historical data
- Try different timeframes
- Check if symbol is actively traded

**5. "Import Error: MetaTrader5"**
```bash
pip install --upgrade MetaTrader5
```

### Getting Help

- 📖 Check the [API Documentation](http://localhost:8001/docs)
- 💬 Open an [Issue](https://github.com/yourusername/mt5-tradebot-api/issues)
- 📧 Contact: your.email@example.com

---

## 🛡️ Risk Warning

**IMPORTANT:** Trading forex and CFDs carries a high level of risk and may not be suitable for all investors. You could lose more than your initial investment.

- ⚠️ Always use a **demo account** for testing
- ⚠️ Never trade with money you cannot afford to lose
- ⚠️ Use proper **risk management** (stop-loss, position sizing)
- ⚠️ Backtest strategies thoroughly before live trading
- ⚠️ Past performance does not guarantee future results

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/mt5-tradebot-api.git

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

## 📞 Contact & Support

- **GitHub:** [@yourusername](https://github.com/yourusername)
- **Email:** your.email@example.com
- **Discord:** [Join our community](https://discord.gg/yourserver)
- **Twitter:** [@yourhandle](https://twitter.com/yourhandle)

---

## 🙏 Acknowledgments

- [MetaTrader 5](https://www.metatrader5.com/) - Trading platform
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pandas](https://pandas.pydata.org/) - Data analysis library
- All contributors who helped improve this project

---

<div align="center">

**Made with ❤️ for the trading community**

[⬆ Back to Top](#-mt5-tradebot-api)

</div>
