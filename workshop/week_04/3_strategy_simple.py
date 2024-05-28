"""
Create a simple strategy to buy and sell periodically.

"""
import logging
from dotenv import load_dotenv
import os
import time
from urllib.parse import urlencode
import hmac
import hashlib
import requests

logging.basicConfig(format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s', level=logging.INFO)
BASE_URL = 'https://testnet.binancefuture.com'
api_URL = '/fapi/v1/order'


# TODO get api key and secret
def get_credentials():
    dotenv_path = 'C:/vault/.testnet_API_secret'
    load_dotenv(dotenv_path=dotenv_path)
    return os.getenv('KEY'), os.getenv('SECRET')


# TODO send market order
def send_market_order(key: str, secret: str, symbol: str, quantity: float, side: bool):
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': symbol,
        'quantity': quantity,
        'side': "BUY" if side else "SELL",
        'timestamp': timestamp,
        'type': 'MARKET',
        'recvWindow': 1000
    }

    query_string = urlencode(params)
    logging.info('Query string: {}'.format(query_string))

    signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = BASE_URL + api_URL + "?" + query_string + "&signature=" + signature

    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": key}
    )
    response = session.post(url=url, params={})

    response_map = response.json()
    orderId = response_map.get('orderId')
    return orderId


# TODO main loop to buy and sell periodically
if __name__ == '__main__':
    api_key, api_secret = get_credentials()

    is_buy = True
    while (1):
        print('1')
        send_market_order(key=api_key, secret=api_secret, symbol='BTCUSDT', quantity=0.1, side=is_buy)
        time.sleep(10)

        is_buy = not is_buy
