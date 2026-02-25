# MT5 Expert Advisor Testing API

A comprehensive RESTful API for testing Expert Advisors (EA) via MetaTrader 5, built with Python and FastAPI.

## Features

- **MT5 Connection Management**: Connect/disconnect to MetaTrader 5 accounts
- **Account Information**: Retrieve real-time account details, balance, equity
- **Position Management**: View open positions, place orders, close positions
- **Historical Data**: Fetch OHLCV data for any symbol and timeframe
- **Backtesting Engine**: Test trading strategies with historical data
- **Strategy Optimization**: Optimize EA parameters automatically
- **Multiple Strategies**: MA Crossover, RSI, MACD, Bollinger Bands support
- **RESTful API**: Easy integration with any programming language
- **Real-time Tick Data**: Get current market prices
- **Trade History**: Access historical deals and orders

## Technology Stack

- **Python 3.8+**
- **FastAPI**: Modern, fast web framework
- **MetaTrader5**: Official MT5 Python library
- **Pandas**: Data analysis and manipulation
- **Uvicorn**: ASGI server

## Installation

### Prerequisites

1. **MetaTrader 5** installed on Windows
2. **Python 3.8+** installed
3. Active MT5 trading account (demo or live)

### Setup

1. **Clone or navigate to the project directory**:
```bash
cd c:\Users\zenox\Desktop\llmfit-v0.4.5-x86_64-pc-windows-msvc
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
copy .env.example .env
```

Edit `.env` file with your MT5 credentials:
```env
MT5_LOGIN=your_login_here
MT5_PASSWORD=your_password_here
MT5_SERVER=your_server_here
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

## Usage

### Start the API Server

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Connection Management

#### Connect to MT5
```http
POST /api/v1/connect
Content-Type: application/json

{
  "login": 12345678,
  "password": "your_password",
  "server": "MetaQuotes-Demo",
  "path": "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
}
```

#### Disconnect from MT5
```http
POST /api/v1/disconnect
```

### Account Information

#### Get Account Details
```http
GET /api/v1/account
```

Response:
```json
{
  "status": "success",
  "data": {
    "login": 12345678,
    "balance": 10000.0,
    "equity": 10000.0,
    "profit": 0.0,
    "margin": 0.0,
    "margin_free": 10000.0
  }
}
```

### Position Management

#### Get Open Positions
```http
GET /api/v1/positions
```

#### Place Order
```http
POST /api/v1/order/place
Content-Type: application/json

{
  "symbol": "EURUSD",
  "order_type": "BUY",
  "volume": 0.1,
  "sl": 1.0500,
  "tp": 1.0700,
  "deviation": 20,
  "magic": 234000,
  "comment": "EA Test Order"
}
```

Order Types:
- `BUY`
- `SELL`
- `BUY_LIMIT`
- `SELL_LIMIT`
- `BUY_STOP`
- `SELL_STOP`

#### Close Position
```http
POST /api/v1/position/close/{position_id}
```

### Market Data

#### Get Historical Data
```http
POST /api/v1/historical-data
Content-Type: application/json

{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59"
}
```

Timeframes:
- `M1`, `M5`, `M15`, `M30` (Minutes)
- `H1`, `H4` (Hours)
- `D1` (Daily)
- `W1` (Weekly)
- `MN1` (Monthly)

#### Get Symbol Tick
```http
GET /api/v1/symbol/EURUSD/tick
```

#### Get All Symbols
```http
GET /api/v1/symbols
```

### Trade History

#### Get Deals History
```http
GET /api/v1/history/deals?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59
```

### Health Check

```http
GET /api/v1/health
```

## Python Client Example

```python
from test_client import MT5APIClient
from datetime import datetime, timedelta

# Initialize client
client = MT5APIClient()

# Connect to MT5
result = client.connect(
    login=12345678,
    password="your_password",
    server="MetaQuotes-Demo"
)
print(result)

# Get account info
account = client.get_account_info()
print(f"Balance: {account['data']['balance']}")

# Get historical data
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
data = client.get_historical_data('EURUSD', 'H1', start_date, end_date)
print(f"Retrieved {data['bars_count']} bars")

# Place a buy order
order = client.place_order(
    symbol='EURUSD',
    order_type='BUY',
    volume=0.1,
    sl=1.0500,
    tp=1.0700
)
print(f"Order placed: {order}")

# Get open positions
positions = client.get_positions()
print(f"Open positions: {positions['count']}")

# Close position
if positions['count'] > 0:
    position_id = positions['data'][0]['ticket']
    result = client.close_position(position_id)
    print(f"Position closed: {result}")

# Disconnect
client.disconnect()
```

## Backtesting & Strategy Testing

The `ea_tester.py` module provides backtesting capabilities:

```python
from ea_tester import EATester
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialize tester
tester = EATester()

# Get historical data
mt5.initialize()
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_H1, start_date, end_date)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Test MA Crossover Strategy
df_strategy = tester.simple_ma_crossover_strategy(df, fast_period=10, slow_period=20)
results = tester.backtest(df_strategy, initial_balance=10000.0, lot_size=0.1)

print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Final Balance: ${results['final_balance']:.2f}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")

# Optimize parameters
optimization = tester.optimize_parameters(df, strategy_type='ma_crossover')
print(f"Best Parameters: {optimization['best_params']}")
print(f"Best Result: ${optimization['best_result']['final_balance']:.2f}")
```

## Available Strategies

### 1. MA Crossover Strategy
- Fast and slow moving average crossover
- Buy signal: Fast MA crosses above Slow MA
- Sell signal: Fast MA crosses below Slow MA

### 2. RSI Strategy
- Relative Strength Index based
- Buy signal: RSI < oversold level (default 30)
- Sell signal: RSI > overbought level (default 70)

### 3. Custom Strategy
You can add custom indicators using the `calculate_indicators()` method:
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (symbol/position not found)
- `500`: Internal Server Error (MT5 connection issues)

Example error response:
```json
{
  "detail": "Not connected to MT5"
}
```

## Security Considerations

1. **Never commit `.env` file** with real credentials
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Implement authentication** for production use
5. **Restrict API access** using firewall rules
6. **Use demo accounts** for testing

## Troubleshooting

### MT5 Connection Failed
- Ensure MetaTrader 5 is installed
- Verify credentials are correct
- Check if MT5 terminal is running
- Enable "Allow DLL imports" in MT5 settings

### Import Error: MetaTrader5
```bash
pip install --upgrade MetaTrader5
```

### Port Already in Use
Change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## Performance Tips

1. **Limit historical data requests** to necessary timeframes
2. **Use appropriate timeframes** for backtesting
3. **Implement caching** for frequently accessed data
4. **Close unused connections** to free resources
5. **Monitor memory usage** during optimization

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is provided as-is for educational and testing purposes.

## Disclaimer

**IMPORTANT**: This software is for testing and educational purposes only. Trading forex and CFDs carries a high level of risk. Never trade with money you cannot afford to lose. Always test strategies on demo accounts before live trading.

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the example client code
3. Verify MT5 connection settings
4. Check MetaTrader 5 terminal logs

## Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Advanced risk management features
- [ ] Multi-account support
- [ ] Machine learning strategy optimization
- [ ] Performance analytics dashboard
- [ ] Trade journal and reporting
- [ ] Alert system for trade signals
- [ ] Integration with TradingView

---

**Happy Trading! 📈**
