"""

Create a method to send market order. User will specify the following parameters:
    - api key
    - api secret
    - price
    - size
    - side (True=buy, False=sell)

"""
import hashlib
import logging
import time
import hmac
from urllib.parse import urlencode
import requests

BASE_URL = 'https://testnet.binancefuture.com'
api_url = '/fapi/v1/order'
logging.basicConfig(format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s', level=logging.INFO)


# TODO
def send_market_order(key: str, secret: str, symbol: str, quantity: float, side: bool):
    timestamp = int(time.time() * 1000)

    order_params = {
        'symbol': symbol,
        'quantity': quantity,
        'type': 'MARKET',
        'side': 'BUY' if side else 'SELL',
        'recvWindow': 5000,
        'timestamp': timestamp
    }

    query_string = urlencode(order_params)
    logging.info('Query string: {}'.format(query_string))

    signature = hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = BASE_URL + api_url + "?" + query_string + "&signature=" + signature

    session = requests.session()
    session.headers.update(
        {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": key}
    )

    response = session.post(url=url, params={})

    response_pretty = response.json()
    order_id = response_pretty.get('orderId')
    print(order_id)

    return order_id


if __name__ == '__main__':
    api_key = '290e05900cf1de7842447837c46ba9ed88d1d1857eab9643d449b6a5abd4e3a9'
    api_secret = '31001b513c6709e4754d36924e7599d562bd48c676aedda6ff9f6b03cbfa2e15'
    send_market_order(api_key, api_secret, 'BTCUSDT', 0.01, True)
