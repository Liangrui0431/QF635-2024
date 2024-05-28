
import logging
import os
import time
from dotenv import load_dotenv
from urllib.parse import urlencode
import hmac
import hashlib
import requests

# logging configuration
logging.basicConfig(format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s', level=logging.INFO)

# URLs
BASE_URL = 'https://testnet.binancefuture.com'


class Tier:
    def __init__(self, price: float, size: float, quote_id: str = None):
        self.price = price
        self.size = size
        self.quote_id = quote_id


# OderBook class to hold bids and asks, as an array of Tiers
class OrderBook:
    def __init__(self, _timestamp: float, _bids: [Tier], _asks: [Tier]):
        self.timestamp = _timestamp
        self.bids = _bids
        self.asks = _asks

    # method to get best bid
    def best_bid(self):
        return self.bids[0].price

    # method to get best ask
    def best_ask(self):
        return self.asks[0].price


# parse JSON object to an order book
def parse(json_object: {}) -> OrderBook:
    # process bids side
    bids = []
    for level in json_object['bids']:

        _price = float(level[0])
        _size = float(level[1])
        tier = Tier(_price, _size)
        bids.append(tier)

    # process asks side
    asks = []
    for level in json_object['asks']:
        _price = float(level[0])
        _size = float(level[1])
        tier = Tier(_price, _size)
        asks.append(tier)

    # "T" or "Trade time" is the time of the transaction in milliseconds, divide by 1000 to convert to seconds
    _event_time = float(json_object['T']) / 1000
    return OrderBook(_event_time, bids, asks)


def get_depth(sym: str):
    response = requests.get(BASE_URL + '/fapi/v1/depth', params={'symbol': sym})
    return parse(response.json())


def get_credentials():
    # dotenv_path = '/vault/binance_keys'
    dotenv_path = 'C:/vault/.testnet_API_secret'

    load_dotenv(dotenv_path=dotenv_path)
    # return api key and secret as tuple
    # return os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET')
    return os.getenv('KEY'), os.getenv('SECRET')


def sign_url(secret: str, api_url, params: {}):
    # create query string
    query_string = urlencode(params)

    # signature
    signature = hmac.new(secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    # url
    return BASE_URL + api_url + "?" + query_string + "&signature=" + signature


def send_market_order(key: str, secret: str, sym: str, quantity: float, side: bool):
    # order parameters
    timestamp = int(time.time() * 1000)
    side_str = "BUY" if side else "SELL"
    order_params = {
        "symbol": sym,
        "side": side_str,
        "type": "MARKET",
        "quantity": quantity,
        'timestamp': timestamp,
        'recvWindow':5000
    }

    logging.info(
        'Sending market order: Symbol: {}, Side: {}, Quantity: {}'.
        format(symbol, side_str, quantity)
    )

    # new order url
    url = sign_url(secret, '/fapi/v1/order', order_params)

    # POST order request
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": key}
    )
    post_response = session.post(url=url, params={})
    post_response_data = post_response.json()

    # GET filled price
    timestamp = int(time.time() * 1000)
    query_params = {
        "symbol": "BTCUSDT",
        "orderId": post_response_data['orderId'],
        "timestamp": timestamp
    }
    url = sign_url(secret, '/fapi/v1/order', query_params)
    get_response = session.get(url=url, params={})
    get_response_data = get_response.json()
    return get_response_data['avgPrice']