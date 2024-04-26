"""
Write a program that periodically get depth message from exchange api, convert to an order book object, and print the
top-of-book prices.

"""

import time
import logging
import requests
from datetime import datetime

logging.basicConfig(format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s', level=logging.INFO)


# Tier represent a price level
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


# define a method that parse json message to order book object
def parse(json_object: {}) -> OrderBook:
    # TODO process bids side
    bids = []
    for level in json_object['bids']:
        _price=level[0]
        _size=level[1]
        tier=Tier(_price, _size)
        bids.append(tier)

    # TODO process asks side
    asks = []
    for level in json_object['asks']:
        _price=level[0]
        _size=level[1]
        tier=Tier(_price, _size)
        asks.append(tier)

    # "T" or "Trade time" is the time of the transaction in milliseconds, divide by 1000 to convert to seconds
    _event_time = float(json_object['T']) / 1000
    return OrderBook(_event_time, bids, asks)


if __name__ == '__main__':

    URL = 'https://fapi.binance.com'

    # https://binance-docs.github.io/apidocs/futures/en/#order-book
    METHOD = '/fapi/v1/depth'


    while True:
        # TODO Get request to get order book snapshot of BTCUSDT
        response = requests.get(URL + METHOD, params={'symbol': 'BTCUSDT'})


        # TODO Get json object from response
        json_object = response.json()

        # TODO call parse() method to convert json message to order book object
        order_book = parse(json_object)

        # TODO print top of book
        print(order_book.best_bid(), order_book.best_ask())

        # TODO sleep 1 second
        time.sleep(1)
