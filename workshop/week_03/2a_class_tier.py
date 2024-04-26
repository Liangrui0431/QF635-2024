"""
Tier represents a price level. Bids and asks are an array of tier.

"""


class Tier:
    def __init__(self, price: float, size: float, quote_id: str = None):
        self.price = price
        self.size = size
        self.quote_id = quote_id

    def __str__(self):
        return '({}, {}, {})'.format(self.price, self.size, self.quote_id)


"""
Order book:
    100,  2     |       101, 5
     99, 50     |       102, 7
     98, 12
"""
# TODO Use Tier class to represent bids and asks in an order book. Compute mid from top-of-book prices.

bids=[Tier(100,2,'b0001'), Tier(99,50,'b0002'), Tier(98,12,'b0003')]
asks=[Tier(101,5,'a0001'), Tier(102,7,'a0002')]

mid=0.5*(bids[0].price+asks[0].price)
print(mid)