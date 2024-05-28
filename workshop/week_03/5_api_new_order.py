"""
Open a paper trading account at Binance Futures Testnet: https://testnet.binancefuture.com/en/futures/BTCUSDT

After login in, there is an "API Key" tab at the bottom section where you will find API Key and API Secret.
Using Notepad or Notepad++, create a file with the following key-value pairs
and saved under directory /vault as "binance_keys"

    BINANCE_API_KEY=<API Key>
    BINANCE_API_SECRET=<API Secret>

Remember to keep these secret and do not share with anyone.

For further information:
https://www.binance.com/en/support/faq/how-to-test-my-functions-on-binance-testnet-ab78f9a1b8824cf0a106b4229c76496d

Reference: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
"""
import os
import time
from dotenv import load_dotenv
from urllib.parse import urlencode
import hmac
import hashlib
import requests

API_KEY = '290e05900cf1de7842447837c46ba9ed88d1d1857eab9643d449b6a5abd4e3a9'
API_SECRET = '31001b513c6709e4754d36924e7599d562bd48c676aedda6ff9f6b03cbfa2e15'

timestamp = int(time.time()*1000)

order_params = {
    'symbol':'BTCUSDT',
    'timestamp': timestamp,
    'side':'SELL',
    'quantity':0.01,
    'type':'MARKET',
    'recvWindow':1000,
}

query_string = urlencode(order_params)
print('Query string: {}'.format(query_string))

signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
print('Signature: {}'.format(signature))

base_url = 'https://testnet.binancefuture.com'
api_url = '/fapi/v1/order'
url = base_url + api_url + "?" + query_string + "&signature=" + signature
print('URL: {}'.format(url))

# POST new order request
session = requests.Session()
session.headers.update(
    {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": API_KEY}
)
response = session.post(url=url, params={})

# if response status is NEW, verify position on web interface - https://testnet.binancefuture.com/en/futures/BTCUSDT
response_data = response.json()
print("Response: {}".format(response_data))

# TODO get order id from response data
order_id=response_data['orderId']


# TODO use order id to query order status and get filled price

timestamp2=int(time.time()*1000)
query_params={
    'symbol':'BTCUSDT',
    'orderId':order_id,
    'timestamp':timestamp2,
    'recvWindow':10000
}
query_string2=urlencode(query_params)
signature2=hmac.new(API_SECRET.encode('utf-8'), query_string2.encode('utf-8'), hashlib.sha256).hexdigest()
url=base_url + api_url +"?" + query_string2 +"&signature="+signature2

get_response=session.get(url=url, params={})
status_data=get_response.json()
print("Response: {}".format(status_data))
print("Filled price: {}".format(status_data['avgPrice']))

