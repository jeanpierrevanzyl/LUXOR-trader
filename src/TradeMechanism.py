import numpy as np
import pandas as pd
#import talib as ta

from abc import ABC, abstractmethod

class TradeMechanism(ABC):

    @abstractmethod
    def sell_signal(self, t):
        pass
    
    @abstractmethod
    def buy_signal(self, t):
        pass

class MovingAverageCrossover(TradeMechanism):

    def __init__(self, price_data, fast_length, slow_length):
        self.price_data = price_data
        self.fast_length = fast_length
        self.slow_length = slow_length
        self.data = pd.DataFrame(columns=["Slow", "Fast"])
        self.data["Slow"] = self.price_data.rolling(window=self.slow_length).mean().values
        self.data["Fast"] = self.price_data.rolling(window=self.fast_length).mean().values
        # self.data["Slow"] = ta.MA(self.price_data, timeperiod=self.slow_length)
        # self.data["Fast"] = ta.MA(self.price_data, timeperiod=self.fast_length)

    def buy_signal(self, t):
        # Second part of if statement comes from ensuring that there is a crossover happening (so that it doesn't negate the effect of the take profit)
        if (self.data["Fast"].iloc[t] >= self.data["Slow"].iloc[t] and self.data["Fast"].iloc[t-1] <= self.data["Slow"].iloc[t-1]):
            return True
        return False

    def sell_signal(self, t):
        if (self.data["Fast"].iloc[t] <= self.data["Slow"].iloc[t]):
            return True
        return False
"""

class BollingerBand(TradeMechanism):
    
    def __init__(self, price_data, time_period, stds):
        self.price_data = price_data
        self.time_period = time_period
        self.stds = stds
        upper, middle, lower = ta.BBANDS(price_data, timeperiod=time_period, nbdevup=stds, nbdevdn=stds, matype=ta.MA_Type.SMA)
        self.data = pd.DataFrame({"Upper": upper, "Middle": middle, "Lower": lower})
    
    def buy_signal(self, t):
        # Once again interference from the take profit limit order
        if (self.price_data.iloc[t] >= self.data["Upper"].iloc[t]):# and self.price_data.iloc[t-1] <= self.data["Upper"].iloc[t-1]):
            return True
        return False
    
    def sell_signal(self, t):
        if (self.price_data.iloc[t] <= self.data["Lower"].iloc[t]):
            return True
        return False

class RelativeStrengthIndex(TradeMechanism):

    def __init__(self, price_data, time_period):
        self.price_data = price_data
        rsi = ta.RSI(price_data, time_period)
        self.data = pd.DataFrame({"RSI": rsi})

    def buy_signal(self, t):
        if (self.data["RSI"].iloc[t] <= 30):
            return True
        return False

    def sell_signal(self, t):
        if (self.data["RSI"].iloc[t] >= 70):
            return True
        return False

class Momentum(TradeMechanism):

    def __init__(self, price_data, time_period):
        self.price_data = price_data
        mom = ta.MOM(price_data, time_period)
        self.data = pd.DataFrame({"Momentum": mom})

    def buy_signal(self, t):
        if (self.data["Momentum"].iloc[t] > 10):
            return True
        return False

    def sell_signal(self, t):
        if (self.data["Momentum"].iloc[t] < -10):
            return True
        return False
"""
