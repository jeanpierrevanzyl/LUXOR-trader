import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.DataReader import *
from src.Visualiser import *
from src.Trader import *
from test.MCS import *

reader = DataReader("./resources/DAT_XLSX_USDZAR_M1_2019.csv")
# reader = DataReader("./resources/SPY.csv")
# reader = DataReader("./resources/gemini_BTCUSD_1hr.csv")

indicators = pd.DataFrame()

mac = MovingAverageCrossover(reader.data["Close"], 10, 30)
# bbs = BollingerBand(reader.data["Close"], 90, 1)
# rsi = RelativeStrengthIndex(reader.data["Close"], 20)
# mom = Momentum(reader.data["Close"], 150)

idtf = IntradayTimeFilter("00:00", "00:00")
slp = 0.3*100
tlp = 0.8*100
tpp = 1.5*100

print("** Starting Trader ***")
trader = Trader(reader.data, starting_capital=1000, trading_mechanism=mac, intraday_time_filter=idtf,
                stop_loss_percent=slp, trailing_loss_percent=tlp, take_profit_percent=tpp)
output_title = f"../nmrqltrading_results/results/{trader.trading_mechanism.fast_length}_{trader.trading_mechanism.slow_length}_{trader.stop_loss_percent}_{trader.trailing_loss_percent}_{trader.take_profit_percent}"
os.makedirs(output_title, exist_ok=True)
print("** Processing trades **")
tr = process_trade_results(trader)
f = open(f"{output_title}/trade_results.txt", 'w')
f.write(tr)
f.flush()
f.close()
print("** Running MCS **")
mcs = MCS(trader, 3)
print("** Plotting Trades Made **")
plot_made_trades(trader)
plt.savefig(f"{output_title}/made_trades.png")
plt.close()
print("** Plotting Equity Curve **")
plot_equity(trader)
plt.savefig(f"{output_title}/equity_curve.png")
plt.close()
print("** Plotting Drawdown Curve **")
plot_drawdown(trader)
plt.savefig(f"{output_title}/drawdown_curve.png")
plt.close()
print("** Plotting MCS **")
plot_monte_carlo(mcs)
plt.savefig(f"{output_title}/mcs.png")
plt.close()
print("** Plotting MAE **")
plot_mae(trader)
plt.savefig(f"{output_title}/mae.png")
plt.close()
print("** Plotting MFE **")
plot_mfe(trader)
plt.savefig(f"{output_title}/mfe.png")
plt.close()
print("** Plots completed **")
