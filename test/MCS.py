import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import random

class MCS:

    def __init__(self, trader, k):
        self.trader = trader
        self.k = k
        self.alternative_equities = pd.DataFrame()
        self.alternative_equities["Date"] = self.trader.data["Date"]
        self.alternative_equities["True"] = self.trader.wallet.data["Equity"]
        self.max_equities = [0] * (self.k+1)

        self.drawdowns = pd.DataFrame(columns=[str(i) for i in range(1, self.k+1)])
        self.drawdowns["Date"] = self.trader.data["Date"]
        self.drawdowns["True"] = self.trader.wallet.data["Drawdown"]

        self.generate_alternatives()
        self.calculate_drawdowns()

    def generate_alternatives(self):
        true_deltas = [0] * len(self.trader.data)
        for i in range(1, len(self.trader.wallet.data["Equity"])):
            true_deltas[i] = self.trader.wallet.data["Equity"].iloc[i] - self.trader.wallet.data["Equity"].iloc[i-1]

        for i in range(1, self.k + 1):
            rand_deltas = random.sample(true_deltas[1:], len(true_deltas[1:]))
            rand_equity = [0] * len(true_deltas)
            rand_equity[0] = self.trader.wallet.data["Equity"].iloc[0]
            for j in range(len(rand_deltas)):
                rand_equity[j+1] = rand_equity[j] + rand_deltas[j]
            self.alternative_equities[str(i)] = rand_equity
        self.alternative_equities.index = self.trader.data.index
    
    def calculate_drawdowns(self):
        for t in range(len(self.alternative_equities)):
            for i in range(1, self.k+1):
                if (self.alternative_equities[str(i)].iloc[t] > self.max_equities[i]):
                    self.max_equities[i] = self.alternative_equities[str(i)].iloc[t]
                self.drawdowns[str(i)].iloc[t] = (self.alternative_equities[str(i)].iloc[t] - self.max_equities[i]) / self.max_equities[i]

