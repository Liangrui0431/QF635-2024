"""
Lists are used to store multiple items in a single variable.
It is a collection which is ordered and changeable. Allows duplicate members.

We can use a list to store bid and ask prices of an order book
"""

# bid prices
bid_prices = [100, 99, 98]

# TODO add some ask prices
ask_prices = [110,108,103]

# TODO sort ask prices
print(sorted(ask_prices))

# TODO get best bid
best_bid=sorted(bid_prices, reverse=True)[0]
print(best_bid)

# TODO get best offer
best_offer=sorted(ask_prices, reverse=False)[0]
print(best_offer)

# TODO compute mid from best bid and offer
mid_price=0.5*(best_bid+best_offer)


# TODO print mid
print(mid_price)