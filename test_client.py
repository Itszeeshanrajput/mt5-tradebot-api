import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

class MT5APIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def connect(self, login: int, password: str, server: str, path: str = None):
        payload = {
            "login": login,
            "password": password,
            "server": server
        }
        if path:
            payload["path"] = path
        
        response = self.session.post(f"{self.base_url}/connect", json=payload)
        return response.json()
    
    def disconnect(self):
        response = self.session.post(f"{self.base_url}/disconnect")
        return response.json()
    
    def get_account_info(self):
        response = self.session.get(f"{self.base_url}/account")
        return response.json()
    
    def get_positions(self):
        response = self.session.get(f"{self.base_url}/positions")
        return response.json()
    
    def get_orders(self):
        response = self.session.get(f"{self.base_url}/orders")
        return response.json()
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: float = None, sl: float = None, tp: float = None,
                   deviation: int = 20, magic: int = 234000, comment: str = "EA Test"):
        payload = {
            "symbol": symbol,
            "order_type": order_type,
            "volume": volume,
            "deviation": deviation,
            "magic": magic,
            "comment": comment
        }
        if price:
            payload["price"] = price
        if sl:
            payload["sl"] = sl
        if tp:
            payload["tp"] = tp
        
        response = self.session.post(f"{self.base_url}/order/place", json=payload)
        return response.json()
    
    def close_position(self, position_id: int):
        response = self.session.post(f"{self.base_url}/position/close/{position_id}")
        return response.json()
    
    def get_historical_data(self, symbol: str, timeframe: str, 
                           start_date: datetime, end_date: datetime):
        payload = {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        response = self.session.post(f"{self.base_url}/historical-data", json=payload)
        return response.json()
    
    def get_symbols(self):
        response = self.session.get(f"{self.base_url}/symbols")
        return response.json()
    
    def get_symbol_tick(self, symbol: str):
        response = self.session.get(f"{self.base_url}/symbol/{symbol}/tick")
        return response.json()
    
    def get_deals_history(self, start_date: datetime, end_date: datetime):
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        response = self.session.get(f"{self.base_url}/history/deals", params=params)
        return response.json()
    
    def health_check(self):
        response = self.session.get(f"{self.base_url}/health")
        return response.json()


if __name__ == "__main__":
    client = MT5APIClient()
    
    print("=== MT5 API Test Client ===\n")
    
    print("1. Health Check")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print("\n" + "="*50 + "\n")
    
    print("2. Connect to MT5")
    print("Please update the credentials below:")
    print("login = YOUR_LOGIN")
    print("password = 'YOUR_PASSWORD'")
    print("server = 'YOUR_SERVER'")
    print("\n" + "="*50 + "\n")
    
    print("3. Example: Get Account Info")
    print("account_info = client.get_account_info()")
    print("\n" + "="*50 + "\n")
    
    print("4. Example: Get Historical Data")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    print(f"data = client.get_historical_data('EURUSD', 'H1', start_date, end_date)")
    print("\n" + "="*50 + "\n")
    
    print("5. Example: Place Order")
    print("order = client.place_order(")
    print("    symbol='EURUSD',")
    print("    order_type='BUY',")
    print("    volume=0.1,")
    print("    sl=1.0500,")
    print("    tp=1.0700")
    print(")")
    print("\n" + "="*50 + "\n")
    
    print("6. Example: Get Positions")
    print("positions = client.get_positions()")
    print("\n" + "="*50 + "\n")
    
    print("7. Example: Close Position")
    print("result = client.close_position(position_id=123456)")
