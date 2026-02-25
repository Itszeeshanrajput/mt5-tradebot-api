import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001/api/v1"

MT5_LOGIN = 262323581
MT5_PASSWORD = "@Zeeshan786"
MT5_SERVER = "Exness-MT5Trial16"

def test_api():
    print("=" * 60)
    print("MT5 API Connection Test")
    print("=" * 60)
    print(f"\nCredentials:")
    print(f"  Login: {MT5_LOGIN}")
    print(f"  Server: {MT5_SERVER}")
    print(f"  Password: {'*' * len(MT5_PASSWORD)}")
    print("\n" + "=" * 60)
    
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
        print("\n   ⚠️  API server is not running!")
        print("   Please start the server first: python main.py")
        return
    
    print("\n2. Testing MT5 Connection...")
    try:
        payload = {
            "login": MT5_LOGIN,
            "password": MT5_PASSWORD,
            "server": MT5_SERVER
        }
        response = requests.post(f"{BASE_URL}/connect", json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print("\n   ✅ Successfully connected to MT5!")
        else:
            print("\n   ❌ Connection failed!")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    print("\n3. Testing Get Account Info...")
    try:
        response = requests.get(f"{BASE_URL}/account", timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and 'data' in result:
            account = result['data']
            print(f"\n   Account Details:")
            print(f"   - Login: {account.get('login', 'N/A')}")
            print(f"   - Balance: ${account.get('balance', 0):.2f}")
            print(f"   - Equity: ${account.get('equity', 0):.2f}")
            print(f"   - Profit: ${account.get('profit', 0):.2f}")
            print(f"   - Margin: ${account.get('margin', 0):.2f}")
            print(f"   - Free Margin: ${account.get('margin_free', 0):.2f}")
            print(f"   - Leverage: 1:{account.get('leverage', 0)}")
            print(f"   - Currency: {account.get('currency', 'N/A')}")
        else:
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n4. Testing Get Symbols...")
    try:
        response = requests.get(f"{BASE_URL}/symbols", timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and 'data' in result:
            symbols = result['data']
            print(f"   Total Symbols: {result.get('count', 0)}")
            print(f"   First 5 symbols:")
            for symbol in symbols[:5]:
                print(f"   - {symbol['name']}: {symbol.get('description', 'N/A')}")
        else:
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n5. Testing Get Current Tick (EURUSD)...")
    try:
        response = requests.get(f"{BASE_URL}/symbol/EURUSD/tick", timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and 'data' in result:
            tick = result['data']
            print(f"   EURUSD Current Price:")
            print(f"   - Bid: {tick.get('bid', 0):.5f}")
            print(f"   - Ask: {tick.get('ask', 0):.5f}")
            print(f"   - Spread: {(tick.get('ask', 0) - tick.get('bid', 0)) * 10000:.1f} pips")
            print(f"   - Time: {datetime.fromtimestamp(tick.get('time', 0))}")
        else:
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n6. Testing Get Positions...")
    try:
        response = requests.get(f"{BASE_URL}/positions", timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print(f"   Open Positions: {result.get('count', 0)}")
            if result.get('count', 0) > 0:
                for pos in result['data']:
                    print(f"   - {pos.get('symbol', 'N/A')}: {pos.get('type', 'N/A')} {pos.get('volume', 0)} lots, Profit: ${pos.get('profit', 0):.2f}")
            else:
                print("   No open positions")
        else:
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n7. Testing Get Historical Data (EURUSD H1, last 100 bars)...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        payload = {
            "symbol": "EURUSD",
            "timeframe": "H1",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        response = requests.post(f"{BASE_URL}/historical-data", json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and 'bars_count' in result:
            print(f"   Bars Retrieved: {result['bars_count']}")
            if result['bars_count'] > 0:
                first_bar = result['data'][0]
                last_bar = result['data'][-1]
                print(f"   First Bar: {first_bar['time']} - O:{first_bar['open']:.5f} H:{first_bar['high']:.5f} L:{first_bar['low']:.5f} C:{first_bar['close']:.5f}")
                print(f"   Last Bar:  {last_bar['time']} - O:{last_bar['open']:.5f} H:{last_bar['high']:.5f} L:{last_bar['low']:.5f} C:{last_bar['close']:.5f}")
        else:
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API Test Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Check the API documentation at: http://localhost:8001/docs")
    print("2. Try placing test orders (use demo account!)")
    print("3. Run backtests with ea_tester.py")
    print("4. Explore advanced strategies in advanced_strategies.py")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
