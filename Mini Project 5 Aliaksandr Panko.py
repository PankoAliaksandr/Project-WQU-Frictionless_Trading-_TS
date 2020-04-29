# Libraries
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from pandas_datareader import data as pdr


# Class
class Trades:

    # Constructor
    def __init__(self, index, start_date, end_date, broker_transact_percent):
        self.__index = '^DJI'
        self.__start_date = start_date
        self.__end_date = end_date
        self.__broker_transact_percent = broker_transact_percent
        self.__index_data = pd.DataFrame()
        self.__returns_ideal = list()
        self.__cum_returns_ideal = list()
        self.__returns_real = list()
        self.__cum_returns_real = list()

    def __download_data(self):
        self.__index_data = pdr.get_data_yahoo(self.__index,
                                               self.__start_date,
                                               self.__end_date)

    def __ideal_trading(self):
        prices = self.__index_data['Close']
        dema20 = prices.ewm(ignore_na=False, span=20, adjust=False).mean()
        start_price = None
        long_position = None
        for i in range(len(prices)-1):
            if ((prices[i] > dema20[i] and
                 prices[i+1] < dema20[i+1]) or
                (prices[i] < dema20[i] and
                 prices[i+1] > dema20[i+1])):
                if start_price is not None:
                    if long_position is True:
                        trade_return = (dema20[i+1]-start_price) / start_price
                    else:
                        trade_return = (start_price-dema20[i+1]) / start_price
                    self.__returns_ideal.append(trade_return)
                start_price = prices[i+1]
                if (prices[i] < dema20[i] and prices[i+1] > dema20[i+1]):
                    # Buy
                    long_position = True
                elif (prices[i] > dema20[i] and prices[i+1] < dema20[i+1]):
                    # Sell
                    long_position = False

    def __real_trading(self):
        prices = self.__index_data['Close']
        open_prices = self.__index_data['Open']
        high_prices = self.__index_data['High']
        low_prices = self.__index_data['Low']
        dema20 = prices.ewm(ignore_na=False, span=20, adjust=False).mean()
        start_price = None
        long_position = None
        for i in range(len(prices)-2):
            if ((prices[i] > dema20[i] and
                 prices[i+1] < dema20[i+1]) or
                (prices[i] < dema20[i] and
                 prices[i+1] > dema20[i+1])):
                if start_price is not None:
                    # Exit the trade
                    slippage_price_exit =\
                     round(dema20[i+1] +
                           0.2 * (prices[i+1] - open_prices[i+1]) +
                           0.05 * (high_prices[i+1] - low_prices[i+1]), 2)
                    broker_commis_exit = self.__broker_transact_percent *\
                        slippage_price_exit
                    if long_position is True:
                        exit_price = slippage_price_exit - broker_commis_exit
                        trade_return = (exit_price-start_price) / start_price
                    else:
                        exit_price = slippage_price_exit + broker_commis_exit
                        trade_return = (start_price-exit_price) / start_price
                    self.__returns_real.append(trade_return)
                slippage_price_enter =\
                    round(open_prices[i+2] +
                          0.2 * (prices[i+2] - open_prices[i+2]) +
                          0.05 * (high_prices[i+2] - low_prices[i+2]), 2)
                broker_commis_exit = self.__broker_transact_percent *\
                    slippage_price_enter
                if (prices[i] < dema20[i] and prices[i+1] > dema20[i+1]):
                    long_position = True
                    start_price = slippage_price_enter + broker_commis_exit
                elif (prices[i] > dema20[i] and prices[i+1] < dema20[i+1]):
                    long_position = False
                    start_price = slippage_price_enter - broker_commis_exit

    def __calculate_cum_ideal_returns(self):
        self.__cum_returns_ideal.append(1)
        cum_sum = 1
        for i in range(len(self.__returns_ideal)):
            cum_sum = cum_sum*(1+self.__returns_ideal[i])
            self.__cum_returns_ideal.append(cum_sum)

    def __calculate_cum_real_returns(self):
        self.__cum_returns_real.append(1)
        cum_sum = 1
        for i in range(len(self.__returns_real)):
            cum_sum = cum_sum*(1+self.__returns_real[i])
            self.__cum_returns_real.append(cum_sum)

    def __visualize(self):
        plt.plot(self.__cum_returns_ideal, label='Ideal Trading',
                 color='r')
        plt.plot(self.__cum_returns_real, label='Real Trading', color='g')
        plt.title("Cumulative Returns")
        plt.xlabel('Trades')
        plt.legend()
        plt.show()

    def main(self):
        self.__download_data()
        self.__ideal_trading()
        self.__real_trading()
        self.__calculate_cum_ideal_returns()
        self.__calculate_cum_real_returns()
        self.__visualize()


index = '^DJI'
end_date = datetime.date.today()
start_date = datetime.date(end_date.year - 15, end_date.month, end_date.day)
broker_transact_percent = 0.0008
trades = Trades(index, start_date, end_date, broker_transact_percent)
trades.main()
