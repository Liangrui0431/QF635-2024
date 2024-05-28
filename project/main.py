from pairs_trading import universe, pairs, trading_df

# import yfinance as yf
# yf.pdr_override()

import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":

    tickers = [
        'MSFT', 'AAPL', 'NVDA', 'GOOGL', 'AMZN', 'META', 'LLY', 'AVGO', 'JPM', 'V', 'XOM', 'WMT', 'MA', 'PG', 'JNJ'
    ]
    start = '2020-01-01'
    end = '2024-01-01'

    u1 = universe(tickers, start, end)

    all_pairs = u1.pairs

    for i in range(len(u1.pairs)):
            pair1 = pairs(u1.data[u1.pairs[i][0]], u1.data[u1.pairs[i][1]])
            # pair1.plot_spread()

            trade1 = trading_df(pair1)
            trade1.get_signal()if __name__ == "__main__":
            trade1.cal_return()
            trade1.get_PnL()