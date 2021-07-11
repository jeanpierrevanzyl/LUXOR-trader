from abc import ABC, abstractmethod
from datetime import datetime

class LimitOrder(ABC):

    def __init__(self, entry_price, threshold):
        self.entry_price = entry_price
        self.threshold = threshold
        self.is_enabled = threshold != None

    @abstractmethod
    def sell_signal(self):
        pass

class StopLoss(LimitOrder):

    def sell_signal(self, current_price):
        if (self.is_enabled and (current_price - self.entry_price) / self.entry_price <= -1 * self.threshold):
            return True
        return False

class TrailingStop(LimitOrder):

    def sell_signal(self, current_price):
        if (self.is_enabled and (current_price - self.entry_price) / self.entry_price <= -1 * self.threshold):
            return True
        return False

    def update_target_price(self, new_target_price):
        if (new_target_price > self.entry_price):
            self.entry_price = new_target_price

class TakeProfit(LimitOrder):

    def sell_signal(self, current_price):
        if (self.is_enabled and (current_price - self.entry_price) / self.entry_price >= self.threshold):
            return True
        return False

class IntradayTimeFilter:

    def __init__(self, start_time, stop_time):
        self.start_time = datetime.strptime(start_time, "%H:%M%S")
        self.stop_time = datetime.strptime(stop_time, "%H:%M%S")
        self.start_time = self.start_time.time()
        self.stop_time = self.stop_time.time()
        self.is_disabled = self.start_time == self.stop_time
        self.hold_trades = False

    def is_valid_trading_time(self, time):
        if (self.is_disabled or (time.time() >= self.start_time and time.time() <= self.stop_time)):
            return True
        return False