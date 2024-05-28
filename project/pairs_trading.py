
import yfinance as yf
import pandas_datareader as pdr

yf.pdr_override()

from statsmodels.tsa.stattools import coint, adfuller
import statsmodels.api as sm
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

class universe:
    def __init__(self, tickers, start, end):
        self.tickers = tickers
        self.start = start
        self.end = end
        self.data = self.get_data()
        self.pairs = self.find_pairs()

    def get_data(self):
        data = pdr.data.get_data_yahoo(self.tickers, self.start,
                                       self.end)['Adj Close']
        return data

    def find_pairs(self):
        tick_len = len(self.tickers)
        pairs = []
        p_val_arr = np.zeros((tick_len, tick_len))

        for i in range(tick_len):
            for j in range(i + 1, tick_len):
                #         print(tickers[i], tickers[j])
                t_stat, p_value, _ = coint(self.data[self.tickers[i]], self.data[self.tickers[j]])
                p_val_arr[i, j] = p_value
                if p_value < 0.05:
                    pairs.append((self.tickers[i], self.tickers[j]))
        return pairs

    def plot_pairs(self):
        sns.heatmap(
            p_val_arr,
            xticklabels=self.tickers,
            yticklabels=self.tickers,
        )

        plt.title('Cointegration P-Values Heatmap')
        plt.xlabel('Tickers')
        plt.ylabel('Tickers')
        plt.show()


class pairs:
    def __init__(self, Y: pd.DataFrame, X: pd.DataFrame, tt_ratio=0.8, entrance_std=1, exit_std=2.5):
        self.Y = Y
        self.X = X
        self.tt_ratio = tt_ratio
        self.entrance_std = entrance_std
        self.exit_std = exit_std
        self.Y_train, self.Y_test, self.X_train, self.X_test = self.tt_split(
        )
        self.results = self.train()
        self.a = self.results.params.iloc[0]
        self.b = self.results.params.iloc[1]
        self.test_residual = self.Y_test - self.b * self.X_test
        self.train_residual_mean, self.train_residual_std = self.create_band()
        self.zscore = (self.test_residual -
                       self.train_residual_mean) / self.train_residual_std

    def tt_split(self):
        train_size = int(self.tt_ratio * len(self.Y))
        Y_train, Y_test = self.Y.iloc[:train_size], self.Y.iloc[train_size:]
        X_train, X_test = self.X.iloc[:train_size], self.X.iloc[train_size:]
        return Y_train, Y_test, X_train, X_test

    def plot_raw(self):
        self.Y.plot()
        self.X.plot()

    def train(self):
        X_train_cons = sm.add_constant(self.X_train)
        results = sm.OLS(self.Y_train, X_train_cons).fit()
        # print(results.summary())
        return results

    def create_band(self)-> tuple[int, int]:
        train_residual_mean = (self.Y_train - self.b * self.X_train).mean()
        train_residual_std = (self.Y_train - self.b * self.X_train).std()
        return train_residual_mean, train_residual_std

    def plot_spread(self, test=True):
        f, ax = plt.subplots()
        f.set_figheight(9)
        f.set_figwidth(16)

        #plot modified prices
        plt.subplot(2, 1, 1)
        plt.plot(self.Y_test, label='Y')
        plt.plot(self.X_test * self.b + self.a, label='altered_X')
        plt.legend()

        #plot spread or residual
        plt.subplot(2, 1, 2)
        if test:
            zscore = (self.test_residual -
                      self.train_residual_mean) / self.train_residual_std
            plt.plot(zscore, color='g')
            plt.legend(['z-score of spread'])

            plt.axhline(0, color="black")
            plt.axhline(self.entrance_std, color='red')
            plt.axhline(-self.entrance_std, color='red')
            plt.axhline(self.exit_std, color='cyan')
            plt.axhline(-self.exit_std, color='cyan')
        plt.show()

class trading_df:
    def __init__(self, pairs):
        self.df = pd.concat([pairs.Y_test, pairs.X_test], axis=1)
        self.pairs = pairs

    def get_signal(self):
        #target position:
        #position ==1: short 1 Y, long some X
        #position ==0: dont hold anything
        #position ==-1: long 1Y, short some X
        # self.df['residual'] = self.df['AAPL'] - self.pairs.b * self.df['PG']
        self.df['residual'] = self.df.iloc[:,0] - self.pairs.b * self.df.iloc[0,1]

        self.df['z-score wrt train'] = (
            self.df['residual'] -
            self.pairs.train_residual_mean) / self.pairs.train_residual_std

        #recall that z-score = y - modified x
        conditions = [(self.df['z-score wrt train'] > 1) &
                      (self.df['z-score wrt train'] < 2),
                      (self.df['z-score wrt train'] > -2) &
                      (self.df['z-score wrt train'] < -1)]

        choices = [1, -1]

        self.df['target_position'] = np.select(conditions, choices, default=0)

    def cal_return(self):
        self.df['pos_change'] = self.df['target_position'].diff()
#         self.df['pos_change'].plot()

        self.df['change_to_cash'] = 0

        # long 1*Y, short b*X
        self.df['change_to_cash'] = np.where(
            self.df['pos_change'] == 1,
            self.df.iloc[:,0].shift(-1) - self.pairs.b * self.df.iloc[:,1].shift(-1),
            self.df['change_to_cash'])

        #short 1*Y, short b*X
        self.df['change_to_cash'] = np.where(
            self.df['target_position'].diff() == 1,
            -self.df.iloc[:,0].shift(-1) +
            self.pairs.b * self.df.iloc[:,1].shift(-1), self.df['change_to_cash'])

#         self.df['change_to_cash'].plot()
        self.df['cumu_cash'] = self.df['change_to_cash'].cumsum()
        # self.df['cumu_cash'].plot()
        # plt.show()

    def get_PnL(self):
        print(self.df.columns.tolist()[:2])
        print(self.df['cumu_cash'].iloc[-1])
