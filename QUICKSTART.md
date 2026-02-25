# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure MT5 Credentials

Create a `.env` file (copy from `.env.example`):

```bash
copy .env.example .env
```

Edit `.env` with your MT5 account details:
- `MT5_LOGIN`: Your MT5 account number
- `MT5_PASSWORD`: Your MT5 password
- `MT5_SERVER`: Your broker's server name
- `MT5_PATH`: Path to MT5 terminal (optional)

### Step 3: Start the API

**Option A - Using Python:**
```bash
python main.py
```

**Option B - Using Batch File (Windows):**
```bash
start_api.bat
```

### Step 4: Test the API

Open your browser and go to:
```
http://localhost:8000/docs
```

You'll see the interactive API documentation (Swagger UI).

## 📝 First API Call

### Connect to MT5

```bash
curl -X POST "http://localhost:8000/api/v1/connect" \
  -H "Content-Type: application/json" \
  -d "{
    \"login\": 12345678,
    \"password\": \"your_password\",
    \"server\": \"MetaQuotes-Demo\"
  }"
```

### Get Account Info

```bash
curl http://localhost:8000/api/v1/account
```

### Get Historical Data

```bash
curl -X POST "http://localhost:8000/api/v1/historical-data" \
  -H "Content-Type: application/json" \
  -d "{
    \"symbol\": \"EURUSD\",
    \"timeframe\": \"H1\",
    \"start_date\": \"2024-01-01T00:00:00\",
    \"end_date\": \"2024-01-31T23:59:59\"
  }"
```

## 🐍 Python Client Example

```python
from test_client import MT5APIClient

# Create client
client = MT5APIClient()

# Connect
client.connect(
    login=12345678,
    password="your_password",
    server="MetaQuotes-Demo"
)

# Get account info
account = client.get_account_info()
print(account)

# Get positions
positions = client.get_positions()
print(positions)
```

## 🧪 Test a Trading Strategy

```python
from ea_tester import EATester
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialize
mt5.initialize()
tester = EATester()

# Get data
end = datetime.now()
start = end - timedelta(days=90)
rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H1, start, end)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Run strategy
df_strategy = tester.simple_ma_crossover_strategy(df, 10, 20)
results = tester.backtest(df_strategy, initial_balance=10000.0)

print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Final Balance: ${results['final_balance']:.2f}")
```

## 📊 Available Endpoints

- `POST /api/v1/connect` - Connect to MT5
- `POST /api/v1/disconnect` - Disconnect from MT5
- `GET /api/v1/account` - Get account information
- `GET /api/v1/positions` - Get open positions
- `GET /api/v1/orders` - Get pending orders
- `POST /api/v1/order/place` - Place new order
- `POST /api/v1/position/close/{id}` - Close position
- `POST /api/v1/historical-data` - Get historical data
- `GET /api/v1/symbols` - Get all symbols
- `GET /api/v1/symbol/{symbol}/tick` - Get current tick
- `GET /api/v1/history/deals` - Get trade history
- `GET /api/v1/health` - Health check

## 🔧 Troubleshooting

**Connection Failed?**
- Ensure MT5 is installed
- Check credentials in `.env`
- Verify MT5 terminal is running

**Import Error?**
```bash
pip install --upgrade MetaTrader5
```

**Port in Use?**
Change port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 📚 Next Steps

1. Read the full [README.md](README.md)
2. Explore the API docs at `/docs`
3. Try the example strategies in `ea_tester.py`
4. Check out advanced strategies in `advanced_strategies.py`

---

**Need Help?** Check the full documentation in README.md
