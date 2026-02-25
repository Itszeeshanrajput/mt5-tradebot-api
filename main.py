from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
from enum import Enum
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MT5 Expert Advisor Testing API",
    description="RESTful API for testing Expert Advisors via MetaTrader 5",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"

class TimeFrame(str, Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"

class MT5ConnectionRequest(BaseModel):
    login: int
    password: str
    server: str
    path: Optional[str] = None

class OrderRequest(BaseModel):
    symbol: str
    order_type: OrderType
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    deviation: int = 20
    magic: int = 234000
    comment: str = "EA Test Order"

class HistoricalDataRequest(BaseModel):
    symbol: str
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime

class BacktestRequest(BaseModel):
    symbol: str
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0
    strategy_params: Dict[str, Any] = Field(default_factory=dict)

class MT5Manager:
    def __init__(self):
        self.connected = False
        self.account_info = None
    
    def connect(self, login: int, password: str, server: str, path: Optional[str] = None):
        if path:
            if not mt5.initialize(path=path, login=login, password=password, server=server):
                raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
        else:
            if not mt5.initialize(login=login, password=password, server=server):
                raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
        
        self.connected = True
        self.account_info = mt5.account_info()
        logger.info(f"Connected to MT5 account: {login}")
        return True
    
    def disconnect(self):
        mt5.shutdown()
        self.connected = False
        logger.info("Disconnected from MT5")
    
    def get_account_info(self):
        if not self.connected:
            raise Exception("Not connected to MT5")
        return mt5.account_info()._asdict()
    
    def get_positions(self):
        if not self.connected:
            raise Exception("Not connected to MT5")
        positions = mt5.positions_get()
        if positions is None:
            return []
        return [pos._asdict() for pos in positions]
    
    def get_orders(self):
        if not self.connected:
            raise Exception("Not connected to MT5")
        orders = mt5.orders_get()
        if orders is None:
            return []
        return [order._asdict() for order in orders]

mt5_manager = MT5Manager()

@app.post("/api/v1/connect")
async def connect_mt5(request: MT5ConnectionRequest):
    try:
        mt5_manager.connect(
            login=request.login,
            password=request.password,
            server=request.server,
            path=request.path
        )
        account_info = mt5_manager.get_account_info()
        return {
            "status": "success",
            "message": "Connected to MT5",
            "account_info": account_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/disconnect")
async def disconnect_mt5():
    try:
        mt5_manager.disconnect()
        return {"status": "success", "message": "Disconnected from MT5"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/account")
async def get_account():
    try:
        account_info = mt5_manager.get_account_info()
        return {"status": "success", "data": account_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/positions")
async def get_positions():
    try:
        positions = mt5_manager.get_positions()
        return {"status": "success", "data": positions, "count": len(positions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/orders")
async def get_orders():
    try:
        orders = mt5_manager.get_orders()
        return {"status": "success", "data": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/order/place")
async def place_order(request: OrderRequest):
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="Not connected to MT5")
        
        symbol_info = mt5.symbol_info(request.symbol)
        if symbol_info is None:
            raise HTTPException(status_code=404, detail=f"Symbol {request.symbol} not found")
        
        if not symbol_info.visible:
            if not mt5.symbol_select(request.symbol, True):
                raise HTTPException(status_code=400, detail=f"Failed to select symbol {request.symbol}")
        
        order_type_map = {
            OrderType.BUY: mt5.ORDER_TYPE_BUY,
            OrderType.SELL: mt5.ORDER_TYPE_SELL,
            OrderType.BUY_LIMIT: mt5.ORDER_TYPE_BUY_LIMIT,
            OrderType.SELL_LIMIT: mt5.ORDER_TYPE_SELL_LIMIT,
            OrderType.BUY_STOP: mt5.ORDER_TYPE_BUY_STOP,
            OrderType.SELL_STOP: mt5.ORDER_TYPE_SELL_STOP,
        }
        
        price = request.price if request.price else mt5.symbol_info_tick(request.symbol).ask
        
        order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": request.symbol,
            "volume": request.volume,
            "type": order_type_map[request.order_type],
            "price": price,
            "deviation": request.deviation,
            "magic": request.magic,
            "comment": request.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if request.sl:
            order_request["sl"] = request.sl
        if request.tp:
            order_request["tp"] = request.tp
        
        result = mt5.order_send(order_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise HTTPException(status_code=400, detail=f"Order failed: {result.comment}")
        
        return {
            "status": "success",
            "message": "Order placed successfully",
            "order_id": result.order,
            "result": result._asdict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/position/close/{position_id}")
async def close_position(position_id: int):
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="Not connected to MT5")
        
        positions = mt5.positions_get(ticket=position_id)
        if not positions:
            raise HTTPException(status_code=404, detail=f"Position {position_id} not found")
        
        position = positions[0]
        
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position_id,
            "price": price,
            "deviation": 20,
            "magic": position.magic,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise HTTPException(status_code=400, detail=f"Close failed: {result.comment}")
        
        return {
            "status": "success",
            "message": "Position closed successfully",
            "result": result._asdict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/historical-data")
async def get_historical_data(request: HistoricalDataRequest):
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="Not connected to MT5")
        
        timeframe_map = {
            TimeFrame.M1: mt5.TIMEFRAME_M1,
            TimeFrame.M5: mt5.TIMEFRAME_M5,
            TimeFrame.M15: mt5.TIMEFRAME_M15,
            TimeFrame.M30: mt5.TIMEFRAME_M30,
            TimeFrame.H1: mt5.TIMEFRAME_H1,
            TimeFrame.H4: mt5.TIMEFRAME_H4,
            TimeFrame.D1: mt5.TIMEFRAME_D1,
            TimeFrame.W1: mt5.TIMEFRAME_W1,
            TimeFrame.MN1: mt5.TIMEFRAME_MN1,
        }
        
        rates = mt5.copy_rates_range(
            request.symbol,
            timeframe_map[request.timeframe],
            request.start_date,
            request.end_date
        )
        
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        return {
            "status": "success",
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "bars_count": len(df),
            "data": df.to_dict(orient='records')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/symbols")
async def get_symbols():
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="Not connected to MT5")
        
        symbols = mt5.symbols_get()
        if symbols is None:
            return {"status": "success", "data": [], "count": 0}
        
        symbol_list = [
            {
                "name": s.name,
                "description": s.description,
                "path": s.path,
                "currency_base": s.currency_base,
                "currency_profit": s.currency_profit,
                "currency_margin": s.currency_margin,
                "digits": s.digits,
                "trade_mode": s.trade_mode,
            }
            for s in symbols
        ]
        
        return {"status": "success", "data": symbol_list, "count": len(symbol_list)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/symbol/{symbol}/tick")
async def get_symbol_tick(symbol: str):
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="Not connected to MT5")
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "status": "success",
            "symbol": symbol,
            "data": tick._asdict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/history/deals")
async def get_deals_history(start_date: datetime, end_date: datetime):
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="Not connected to MT5")
        
        deals = mt5.history_deals_get(start_date, end_date)
        if deals is None:
            return {"status": "success", "data": [], "count": 0}
        
        deals_list = [deal._asdict() for deal in deals]
        
        return {"status": "success", "data": deals_list, "count": len(deals_list)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "mt5_connected": mt5_manager.connected,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
