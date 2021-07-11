import numpy as np
import pandas as pd
#import talib as ta
from matplotlib import pyplot as plt

from src.LimitOrder import *
from src.TradeMechanism import *

class Trader:

    def __init__(self, data, starting_capital, trading_mechanism, intraday_time_filter, stop_loss_percent, trailing_loss_percent, take_profit_percent):
        self.data = data
        self.price_data = self.data["Close"]
        self.stop_loss_percent, self.trailing_loss_percent, self.take_profit_percent = stop_loss_percent, trailing_loss_percent, take_profit_percent
        self.intraday_time_filter = intraday_time_filter
        self.trading_mechanism = trading_mechanism
        self.wallet = Wallet(starting_capital, 0, self.data["Date"], self.price_data.iloc[0])

        self.open_trades = []
        self.past_trades = []

        self.t = 1
        self.run_sim()

    def run_sim(self):
        while (self.t < len(self.price_data)):
            if (self.intraday_time_filter.is_valid_trading_time(self.data["Date"].iloc[self.t])):
                if (self.trading_mechanism.buy_signal(self.t)):
                    volume = (self.wallet.cash_balance/self.price_data[self.t]) # cast to int??
                    self.buy_stock(volume)
                self.evaluate_open_trades(self.price_data[self.t])
            
            self.wallet.update_equity_records(self.t, self.price_data.iloc[self.t])

            self.t += 1

    def evaluate_open_trades(self, current_price):
        for trade in self.open_trades:
            trade.update(self.price_data[self.t])
            volume = self.wallet.stock_balance
            sell = False
            if (self.trading_mechanism.sell_signal(self.t)):
                sell = True
            elif (trade.stop_loss.sell_signal(current_price) or trade.trailing_loss.sell_signal(current_price) or trade.take_profit.sell_signal(current_price)):
                sell = True
            elif (not self.intraday_time_filter.hold_trades and not self.intraday_time_filter.is_disabled):
                if (self.data["Date"].iloc[self.t].time() >= self.intraday_time_filter.stop_time):
                    sell = True
            if (sell):
                self.sell_stock(volume)
                trade.sell(self.price_data[self.t])
                self.past_trades.append(trade)
                self.open_trades.remove(trade)
    
    def buy_stock(self, volume):
        if (self.wallet.cash_balance > 0):
            self.wallet.data["Signal"].iloc[self.t] = 1
            self.wallet.data["Trade Volume"].iloc[self.t] = volume
            self.wallet.data["Buy Price"].iloc[self.t] = self.price_data[self.t]

            sl = StopLoss(self.wallet.data["Buy Price"].iloc[self.t], self.stop_loss_percent/100)
            tl = TrailingStop(self.wallet.data["Buy Price"].iloc[self.t], self.trailing_loss_percent/100)
            tp = TakeProfit(self.wallet.data["Buy Price"].iloc[self.t], self.take_profit_percent/100)
            self.open_trades.append(Trade(self.wallet.data["Date"].iloc[self.t], self.price_data[self.t], sl, tl, tp))

            self.wallet.stock_balance += volume
            self.wallet.cash_balance -= volume * self.price_data[self.t]

    def sell_stock(self, volume):
        if (self.wallet.stock_balance > 0):
            self.wallet.data["Signal"].iloc[self.t] = -1
            self.wallet.data["Trade Volume"].iloc[self.t] = volume
            self.wallet.data["Sell Price"].iloc[self.t] = self.price_data[self.t]

            self.wallet.cash_balance += volume * self.price_data[self.t]
            self.wallet.stock_balance -= volume

class Trade:

    def __init__(self, date, buy_price, stop_loss, trailing_loss, take_profit):
        self.date = date
        self.buy_price = buy_price
        self.sell_price = np.nan
        self.mdd = float("inf")
        self.mru = float("-inf")
        self.pl = np.nan
        self.stop_loss = stop_loss
        self.trailing_loss = trailing_loss
        self.take_profit = take_profit
    
    def sell(self, current_price):
        self.sell_price = current_price
        self.pl = (self.buy_price - self.sell_price) / self.buy_price
    
    def update_exit_mechanisms(self, current_price):
        self.trailing_loss.update_target_price(current_price)
    
    def update(self, current_price):
        self.update_exit_mechanisms(current_price)
        if ((self.buy_price - current_price) / self.buy_price < self.mdd):
            self.mdd = (self.buy_price - current_price) / self.buy_price
        if ((self.buy_price - current_price) / self.buy_price > self.mru):
            self.mru = (self.buy_price - current_price) / self.buy_price

class Wallet:

    def __init__(self, cash_balance, stock_balance, date, price):
        self.cash_balance = cash_balance
        self.stock_balance = stock_balance
        
        self.data = pd.DataFrame({"Date": date, "Signal": np.nan, "Trade Volume": np.nan, "Sell Price": np.nan, "Buy Price": np.nan, "Cash Balance": np.nan, "Stock Balance": np.nan, "Equity": np.nan, "Drawdown": np.nan}, date)
        # self.data = pd.DataFrame(columns=["Date", "Signal", "Trade Volume", "Sell Price", "Buy Price", "Cash Balance", "Stock Balance", "Equity", "Drawdown"])
        # self.data.set_index("Date", drop=False, inplace=True)

        self.data.loc[[date[0]], ["Cash Balance", "Stock Balance", "Equity"]] = [self.cash_balance, self.stock_balance, self.cash_balance + (self.stock_balance * price)]
        self.max_equity = self.data["Equity"].iloc[0]
    
    def update_equity_records(self, t, price):
        self.data["Cash Balance"].iloc[t] = self.cash_balance
        self.data["Stock Balance"].iloc[t] = self.stock_balance
        self.data["Equity"].iloc[t] = self.cash_balance + (self.stock_balance * price)
        if (self.data["Equity"].iloc[t] > self.max_equity):
            self.max_equity = self.data["Equity"].iloc[t]
        self.data["Drawdown"].iloc[t] = (self.data["Equity"].iloc[t] - self.max_equity) / self.max_equity

def process_trade_results(trader):
    """ !!! require rework using trader.past_trades !!! """
    sell_prices = trader.wallet.data["Sell Price"].dropna()
    buy_prices = trader.wallet.data["Buy Price"].dropna()
    num_sells = len(sell_prices)
    num_buys = len(buy_prices)
    trades = trader.wallet.data[["Trade Volume", "Buy Price", "Sell Price"]][trader.wallet.data["Trade Volume"].notna()]
    time = len(trades)
    profits = []
    losses = []
    for t in range(1, time, 2):
        equity_bought = trades["Trade Volume"].iloc[t-1] * trades["Buy Price"].iloc[t-1]
        equity_sold = trades["Trade Volume"].iloc[t] * trades["Sell Price"].iloc[t]
        equity_change = equity_sold - equity_bought

        if (equity_change < 0):
            losses.append(equity_change)
        else:
            profits.append(equity_change)
    
    profits = np.array(profits)
    losses = np.array(losses)
    if (len(profits) == 0):
        profits = np.zeros(1)
    if (len(losses) == 0):
        losses = np.zeros(1)
    final_equity = trader.wallet.data["Equity"].iloc[-1]
    headings = "final_equity, num_trades, num_sells, num_buys, num_winners, num_losers, ave_profit, ave_loss, max_profit, max_loss"
    trade_results = f"{headings}\n{final_equity}\n{len(trades)}\n{num_sells}\n{num_buys}\n{len(profits)}\n{len(losses)}\n{np.average(profits)}\n{np.average(losses)}\n{np.max(profits)}\n{np.min(losses)}\n"
    return trade_results