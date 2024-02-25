import asyncio
import json
from threading import Thread
import websockets
from binance.depthcache import FuturesDepthCacheManager
from binance import AsyncClient, BinanceSocketManager, Client
from common.interface_book import VenueOrderBook, PriceLevel, OrderBook
import logging
from common.interface_order import OrderEvent, OrderStatus, ExecutionType, Side
import schedule

logging.basicConfig(format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s', level=logging.INFO)


class BinanceFutureGateway:

    def __init__(self, symbol: str, api_key=None, api_secret=None, name='Binance', testnet=True):
        self._api_key = api_key
        self._api_secret = api_secret
        self._exchange_name = name
        self._symbol = symbol
        self.testnet = testnet

        # binance async client
        self._client = None
        self._async_client = None
        self._dcm = None  # depth cache, which implements the logic to manage a local order book
        self._dws = None  # depth async WebSocket session
        self._listen_key = None

        # depth cache
        self._depth_cache = None

        # this is a loop and dedicated thread to run all async concurrent tasks
        self._loop = asyncio.new_event_loop()
        self._loop_thread = Thread(target=self._run_async_tasks, daemon=True, name=name)

        # callbacks
        self._depth_callbacks = []
        self._execution_callbacks = []

    """
        Connect method to start exchange connection
    """
    def connect(self):
        logging.info('Initializing connection')

        self._loop.run_until_complete(self._reconnect_ws())

        logging.info("starting event loop thread")
        self._loop_thread.start()

        # synchronous client
        self._client = Client(self._api_key, self._api_secret, testnet=self.testnet)

        # job
        schedule.every(15).minutes.do(self._extend_listen_key)

    # an internal method to reconnect websocket
    async def _reconnect_ws(self):
        logging.info("reconnecting websocket")
        self._async_client = await AsyncClient.create(self._api_key, self._api_secret, testnet=self.testnet)

    # an internal method to runs tasks in parallel
    def _run_async_tasks(self):
        """ Run the following tasks concurrently in the current thread """
        self._loop.create_task(self._listen_depth_forever())
        self._loop.create_task(self._listen_execution_forever())
        self._loop.run_forever()

    # an internal async method to listen to depth stream
    async def _listen_depth_forever(self):
        logging.info("Subscribing to depth events")
        while True:
            if not self._dws:
                logging.info("depth socket not connected, reconnecting")
                self._dcm = FuturesDepthCacheManager(self._async_client, symbol=self._symbol)
                self._dws = await self._dcm.__aenter__()

            # wait for depth update
            try:
                self._depth_cache = await self._dws.recv()

                if self._depth_callbacks:
                    # notify callbacks
                    for _callback in self._depth_callbacks:
                        _callback(VenueOrderBook(self._exchange_name, self.get_order_book()))
            except Exception as e:
                logging.exception('encountered issue in depth processing')
                # reset socket and reconnect
                self._dws = None
                await self._reconnect_ws()

    # an internal async method to listen to user data stream
    async def _listen_execution_forever(self):
        logging.info("Subscribing to user data events")
        self._listen_key = await self._async_client.futures_stream_get_listen_key()
        if self.testnet:
            url = 'wss://stream.binancefuture.com/ws/' + self._listen_key
        else:
            url = 'wss://fstream.binance.com/ws/' + self._listen_key

        conn = websockets.connect(url)
        ws = await conn.__aenter__()
        while ws.open:
            _message = await ws.recv()
            # logging.info(_message)

            # convert to json
            _data = json.loads(_message)
            update_type = _data.get('e')

            if update_type == 'ORDER_TRADE_UPDATE':
                _trade_data = _data.get('o')
                _order_id = _trade_data.get('c')
                _symbol = _trade_data.get('s')
                _execution_type = _trade_data.get('x')
                _order_status = _trade_data.get('X')
                _side = _trade_data.get('S')
                _last_filled_price = float(_trade_data.get('L'))
                _last_filled_qty = float(_trade_data.get('l'))

                # create an order event
                _order_event = OrderEvent(_symbol, _order_id, ExecutionType[_execution_type], OrderStatus[_order_status])
                _order_event.side = Side[_side]
                if _execution_type == 'TRADE':
                    _order_event.last_filled_price = _last_filled_price
                    _order_event.last_filled_quantity = _last_filled_qty

                # notify callbacks
                if self._execution_callbacks:
                    # notify callbacks
                    for _callback in self._execution_callbacks:
                        _callback(_order_event)

    def _extend_listen_key(self):
        logging.info("Extending listen key")
        self._client.futures_stream_keepalive(self._listen_key)

    """ 
        Get order book 
    """
    def get_order_book(self) -> VenueOrderBook:
        bids = [PriceLevel(price=p, size=s) for (p, s) in self._depth_cache.get_bids()[:5]]
        asks = [PriceLevel(price=p, size=s) for (p, s) in self._depth_cache.get_asks()[:5]]
        return OrderBook(timestamp=self._depth_cache.update_time, contract_name=self._symbol, bids=bids, asks=asks)

    """
        Place a limit order
    """
    def place_limit_order(self, side: Side, price, quantity, tif='IOC') -> bool:
        try:
            self._client.futures_create_order(symbol=self._symbol,
                                              side=side.name,
                                              type='LIMIT',
                                              price=price,
                                              quantity=quantity,
                                              timeInForce=tif)
            return True
        except Exception as e:
            logging.info("Failed to place order: {}".format(e))
            return False

    """
        Cancel an order
    """
    def cancel_order(self, symbol, order_id) -> bool:
        try:
            self._client.futures_cancel_order(symbol=symbol, origClientOrderId=order_id)
            return True
        except Exception as e:
            logging.warning("Failed to cancel order: {}, {}".format(order_id, e))
            return False

    """ 
        Register a depth callback function that takes one argument: (book: VenueOrderBook) 
    """
    def register_depth_callback(self, callback):
        self._depth_callbacks.append(callback)

    """ 
        Register an execution callback function that takes one argument, an order event: (event: OrderEvent) 
    """
    def register_execution_callback(self, callback):
        self._execution_callbacks.append(callback)
