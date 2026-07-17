from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
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
from enum import Enum
import uvicorn
import logging
import asyncio
import os
from contextlib import asynccontextmanager

from config import settings
from ea_tester import EATester

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

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
    strategy_name: str
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    lot_size: float = 0.1
    stop_loss_pips: float = 0.0
    take_profit_pips: float = 0.0
    exit_on_opposite_signal: bool = True

class OptimizeRequest(BaseModel):
    symbol: str
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0
    strategy_name: str
    param_ranges: Dict[str, List[Any]]
    lot_size: float = 0.1
    stop_loss_pips: float = 0.0
    take_profit_pips: float = 0.0

class AutoTradeStartRequest(BaseModel):
    symbol: str
    timeframe: TimeFrame
    strategy_name: str
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    lot_size: float = 0.01
    stop_loss_pips: float = 0.0
    take_profit_pips: float = 0.0


class MT5Manager:
    def __init__(self):
        self.connected = False
        self.account_info = None
        self.login = None
        self.server = None
    
    def connect(self, login: int, password: str, server: str, path: Optional[str] = None):
        if path:
            if not mt5.initialize(path=path, login=login, password=password, server=server):
                raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
        else:
            if not mt5.initialize(login=login, password=password, server=server):
                raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
        
        self.connected = True
        self.login = login
        self.server = server
        self.account_info = mt5.account_info()
        logger.info(f"Connected to MT5 account: {login}")
        return True
    
    def disconnect(self):
        mt5.shutdown()
        self.connected = False
        self.login = None
        self.server = None
        logger.info("Disconnected from MT5")
    
    def get_account_info(self):
        if not self.connected:
            raise Exception("Not connected to MT5")
        info = mt5.account_info()
        if info is None:
            raise Exception(f"Failed to retrieve account info: {mt5.last_error()}")
        return info._asdict()
    
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


class AutoTrader:
    def __init__(self):
        self.active = False
        self.symbol = "EURUSD"
        self.timeframe = TimeFrame.M1
        self.strategy_name = "rsi"
        self.strategy_params = {"rsi_period": 14, "oversold": 30, "overbought": 70}
        self.lot_size = 0.01
        self.stop_loss_pips = 10.0
        self.take_profit_pips = 20.0
        self.task = None
        self.last_run = None
        self.last_signal = 0
        self.log = []

    def start(self, symbol: str, timeframe: TimeFrame, strategy_name: str, strategy_params: Dict[str, Any], lot_size: float, sl_pips: float, tp_pips: float):
        if self.active:
            raise Exception("Auto-Trader is already running")
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategy_name = strategy_name
        self.strategy_params = strategy_params
        self.lot_size = lot_size
        self.stop_loss_pips = sl_pips
        self.take_profit_pips = tp_pips
        self.active = True
        self.log = [f"[{datetime.now().isoformat()}] Auto-Trader initialized on {symbol} using {strategy_name}"]
        self.task = asyncio.create_task(self.run_loop())
        
    def stop(self):
        if not self.active:
            return
        self.active = False
        if self.task:
            self.task.cancel()
            self.task = None
        self.log.append(f"[{datetime.now().isoformat()}] Auto-Trader stopped")
        
    async def run_loop(self):
        tester = EATester()
        
        while self.active:
            try:
                if not mt5_manager.connected:
                    self.log.append(f"[{datetime.now().isoformat()}] Waiting for MT5 connection...")
                    await asyncio.sleep(10)
                    continue
                    
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
                
                # Fetch enough bars to calculate technical metrics
                rates = mt5.copy_rates_from_pos(
                    self.symbol,
                    timeframe_map[self.timeframe],
                    0,
                    150
                )
                
                if rates is None or len(rates) == 0:
                    self.log.append(f"[{datetime.now().isoformat()}] Error: Could not copy rates for {self.symbol}")
                    await asyncio.sleep(10)
                    continue
                    
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                df_with_signal = tester.run_strategy(df, self.strategy_name, self.strategy_params)
                
                # Select the second to last row as the last completed bar
                latest_bar = df_with_signal.iloc[-2]
                signal = int(latest_bar['signal'])
                close_price = float(latest_bar['close'])
                
                self.last_run = datetime.now().isoformat()
                
                if signal != self.last_signal:
                    self.log.append(f"[{self.last_run}] Signal Alert! Previous: {self.last_signal} | Current: {signal} at Price {close_price}")
                    
                    # Manage open positions for this bot (magic number 888999)
                    positions = mt5_manager.get_positions()
                    bot_positions = [p for p in positions if p.get('symbol') == self.symbol and p.get('magic') == 888999]
                    
                    for pos in bot_positions:
                        should_close = False
                        if pos['type'] == mt5.POSITION_TYPE_BUY and signal <= 0:
                            should_close = True
                        elif pos['type'] == mt5.POSITION_TYPE_SELL and signal >= 0:
                            should_close = True
                            
                        if should_close:
                            self.log.append(f"[{datetime.now().isoformat()}] Closing position {pos['ticket']}")
                            await self.close_live_position(pos)
                            
                    # Enter new position if signal is active (1 or -1)
                    # Fetch positions again to check count
                    positions = mt5_manager.get_positions()
                    bot_positions = [p for p in positions if p.get('symbol') == self.symbol and p.get('magic') == 888999]
                    
                    if len(bot_positions) == 0:
                        if signal == 1:
                            self.log.append(f"[{datetime.now().isoformat()}] Signal Buy! Opening Long order...")
                            await self.open_live_position(OrderType.BUY)
                        elif signal == -1:
                            self.log.append(f"[{datetime.now().isoformat()}] Signal Sell! Opening Short order...")
                            await self.open_live_position(OrderType.SELL)
                            
                    self.last_signal = signal
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log.append(f"[{datetime.now().isoformat()}] Error: {str(e)}")
                logger.error(f"AutoTrader Loop Error: {e}")
                
            await asyncio.sleep(10)
            
    async def open_live_position(self, order_type: OrderType):
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            self.log.append(f"[{datetime.now().isoformat()}] Error: Tick data unavailable for {self.symbol}")
            return
            
        price = tick.ask if order_type == OrderType.BUY else tick.bid
        
        # Calculate SL/TP in pips
        pip_size = 0.0001
        if price > 1000:
            pip_size = 0.1
        elif price > 50:
            pip_size = 0.01
            
        sl = None
        tp = None
        if self.stop_loss_pips > 0:
            sl = price - (self.stop_loss_pips * pip_size) if order_type == OrderType.BUY else price + (self.stop_loss_pips * pip_size)
        if self.take_profit_pips > 0:
            tp = price + (self.take_profit_pips * pip_size) if order_type == OrderType.BUY else price - (self.take_profit_pips * pip_size)
            
        # Ensure symbol is active
        if not mt5.symbol_select(self.symbol, True):
            self.log.append(f"[{datetime.now().isoformat()}] Error: Failed to select symbol {self.symbol}")
            return
            
        order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": mt5.ORDER_TYPE_BUY if order_type == OrderType.BUY else mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": 20,
            "magic": 888999,
            "comment": f"AutoTrade {self.strategy_name}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl:
            order_request["sl"] = sl
        if tp:
            order_request["tp"] = tp
            
        result = mt5.order_send(order_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log.append(f"[{datetime.now().isoformat()}] Order rejected: {result.comment}")
        else:
            self.log.append(f"[{datetime.now().isoformat()}] Order executed! Deal Ticket: {result.order}")
            
    async def close_live_position(self, position):
        order_type = mt5.ORDER_TYPE_SELL if position['type'] == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(position['symbol'])
        if not tick:
            self.log.append(f"[{datetime.now().isoformat()}] Error: Tick data unavailable during close")
            return
            
        price = tick.bid if position['type'] == mt5.ORDER_TYPE_BUY else tick.ask
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position['symbol'],
            "volume": position['volume'],
            "type": order_type,
            "position": position['ticket'],
            "price": price,
            "deviation": 20,
            "magic": 888999,
            "comment": "AutoTrader Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(close_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log.append(f"[{datetime.now().isoformat()}] Close rejected: {result.comment}")
        else:
            self.log.append(f"[{datetime.now().isoformat()}] Position closed! Deal Ticket: {result.order}")


auto_trader = AutoTrader()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-connect on startup if configured
    if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
        logger.info("MT5 credentials found in configuration. Auto-connecting...")
        try:
            mt5_manager.connect(
                login=settings.MT5_LOGIN,
                password=settings.MT5_PASSWORD,
                server=settings.MT5_SERVER,
                path=settings.MT5_PATH
            )
            logger.info("Auto-connection successful!")
        except Exception as e:
            logger.error(f"Auto-connection failed: {e}")
    yield
    # Shutdown logic
    auto_trader.stop()
    if mt5_manager.connected:
        mt5_manager.disconnect()


app = FastAPI(
    title=settings.API_TITLE,
    description="RESTful API for testing Expert Advisors via MetaTrader 5",
    version=settings.API_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Read index.html dynamically to support changes without restarting server
    index_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard file not found! Check templates/index.html</h1>", status_code=404)


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


@app.post("/api/v1/backtest")
async def backtest_strategy(request: BacktestRequest):
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
        
        # Fetch data
        rates = mt5.copy_rates_range(
            request.symbol,
            timeframe_map[request.timeframe],
            request.start_date,
            request.end_date
        )
        
        if rates is None or len(rates) == 0:
            raise HTTPException(status_code=404, detail="No historical data found to run simulation")
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        tester = EATester()
        # Process indicator strategy
        df_processed = tester.run_strategy(df, request.strategy_name, request.strategy_params)
        
        # Execute backtest
        results = tester.backtest(
            df_processed,
            initial_balance=request.initial_balance,
            lot_size=request.lot_size,
            stop_loss_pips=request.stop_loss_pips,
            take_profit_pips=request.take_profit_pips,
            exit_on_opposite_signal=request.exit_on_opposite_signal
        )
        
        return results
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/optimize")
async def optimize_strategy(request: OptimizeRequest):
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
            raise HTTPException(status_code=404, detail="No historical data found for optimization")
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        tester = EATester()
        optimization_results = tester.optimize_parameters(
            df,
            strategy_name=request.strategy_name,
            param_ranges=request.param_ranges
        )
        
        return optimization_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/autotrade/start")
async def start_autotrade(request: AutoTradeStartRequest):
    try:
        if not mt5_manager.connected:
            raise HTTPException(status_code=400, detail="MT5 is not connected. Connect first.")
        
        auto_trader.start(
            symbol=request.symbol,
            timeframe=request.timeframe,
            strategy_name=request.strategy_name,
            strategy_params=request.strategy_params,
            lot_size=request.lot_size,
            sl_pips=request.stop_loss_pips,
            tp_pips=request.take_profit_pips
        )
        return {"status": "success", "message": "Automated Trading started successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/autotrade/stop")
async def stop_autotrade():
    try:
        auto_trader.stop()
        return {"status": "success", "message": "Automated Trading stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/autotrade/status")
async def get_autotrade_status():
    return {
        "active": auto_trader.active,
        "symbol": auto_trader.symbol,
        "timeframe": auto_trader.timeframe,
        "strategy": auto_trader.strategy_name,
        "last_run": auto_trader.last_run,
        "log": auto_trader.log
    }


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
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
