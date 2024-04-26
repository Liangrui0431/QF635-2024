"""
Define a function to calculate mid from bid and offer prices
"""


def calculate_mid(bid_price: float, offer_price: float) -> float:

    return (bid_price+offer_price)/2

mid = calculate_mid(100.50, 101.80)
print(mid)
