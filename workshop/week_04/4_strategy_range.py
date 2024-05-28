"""
Create a range trading strategy

"""
import os
from dotenv import load_dotenv
import logging
import time
import hmac
from urllib.parse import urlencode
import hashlib
import requests

logging.basicConfig(format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s', level=logging.INFO)
BASE_URL = 'https://testnet.binancefuture.com'
api_URL = '/fapi/v1/depth'


#get order book
class Tier:
    def __init__(self, price_, size_, quote_id=0):
        self.price = price_
        self.size = size_
        self.quote_id = quote_id


class Orderbook:
    def __init__(self, timestamp, bids, asks):
        self.timestamp = timestamp
        self.bids = bids
        self.asks = asks

    def best_bid(self):
        return self.bids[0].price

    def best_ask(self):
        return self.asks[0].price


def parse(json_obj):
    bids = []
    for i in json_obj['bids']:
        price = float(i[0])
        size = float(i[1])
        tier = Tier(price, size)
        bids.append(tier)

    asks = []
    for i in json_obj['asks']:
        price = float(i[0])
        size = float(i[1])
        tier = Tier(price, size)
        asks.append(tier)

    event_time = float(json_obj['T']) / 1000
    return Orderbook(event_time, bids, asks)


def get_depth(symbol):
    response = requests.get(BASE_URL + api_URL, params={'symbol': symbol})
    return parse(response.json())


def exe_order(key, secret, symbol, quantity, side):
    timestamp = int(time.time() * 1000)
    side_str="BUY" if side else "SELL"
    params = {
        'symbol': symbol,
        'quantity': quantity,
        'type': 'MARKET',
        'side': side_str,
        'timestamp': timestamp
    }
    logging.info(
        'Sending market order: Symbol: {}, Side: {}, Quantity: {}'.
        format(symbol, side_str, quantity)
    )
    query_string = urlencode(params)
    signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = BASE_URL + '/fapi/v1/order' + "?" + query_string + "&signature=" + signature

    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": key}
    )

    response = session.post(url=url, params={})
    # print(response.json()) or logging.error(response.text)

    response_map = response.json()
    # order_id=response_map.get('orderId')

    timestamp = int(time.time() * 1000)
    params = {
        'symbol': symbol,
        'orderId': response_map['orderId'],
        'timestamp': timestamp
    }
    query_string = urlencode(params)
    signature = hmac.new(secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
    url = BASE_URL + '/fapi/v1/order' + "?" + query_string + "&signature=" + signature
    get_response = session.get(url=url, params={})
    get_response_data = get_response.json()
    return get_response_data['avgPrice']


# get credentials
def get_credentials():
    dotenv_path = 'C:/vault/.testnet_API_secret'
    load_dotenv(dotenv_path=dotenv_path)
    return os.getenv('KEY'), os.getenv('SECRET')


#send order


# execute strategy

if __name__ == '__main__':

    api_key, api_secret = get_credentials()
    symbol = 'BTCUSDT'
    target_quantity = 0.01
    side = True
    current_position = 0
    upper_bound = 62600
    lower_bound = 62500

    #mean reversion strategy
    while True:
        time.sleep(1)
        orderbook = get_depth(symbol)

        #determine target position
        # target_position=0
        if orderbook.best_ask() > upper_bound:
            #short or hold at -0.1 unit
            target_position = -target_quantity
        elif orderbook.best_bid() < lower_bound:
            #long or hold at 0.1 unit
            target_position = target_quantity
        else:
            #clear position
            target_position = 0

        logging.info(
            'Bid: {}, Ask: {}, Position: {}, Target: {}'.
            format(orderbook.best_bid(), orderbook.best_ask(), current_position, target_position)
        )
        #getting to target position
        order_quantity = target_position - current_position
        if order_quantity != 0:
            abs_quantity = abs(order_quantity)
            side = True if order_quantity > 0 else False
            filled_price = exe_order(api_key, api_secret, symbol, abs_quantity, side)
            logging.info('Filled price: {}'.format(filled_price))
            current_position = target_position
        else:
            logging.info("Hold position")
