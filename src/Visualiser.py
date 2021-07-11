import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import mplfinance as mpf

def plot_made_trades(trader):
    fig = mpf.figure(style="charles")
    ax = fig.add_subplot()

    plots = [mpf.make_addplot(trader.data, type="candle", ax=ax),
            mpf.make_addplot(trader.trading_mechanism.data, type="line", ax=ax),
            mpf.make_addplot(trader.wallet.data[["Buy Price"]], type="scatter", ax=ax, color='g', marker='^', markersize=40),
            mpf.make_addplot(trader.wallet.data[["Sell Price"]], type="scatter", ax=ax, color='r', marker='v', markersize=40)]
    mpf.plot(trader.data, ax=ax, addplot=plots)
    ax.legend(list(trader.trading_mechanism.data.columns.values) + ["_", "_", "_", "_", "_", "Buy", "Sell"])
    ax.set_title("Trades made compared to price data and moving averages")
    return fig
    # plt.savefig(f"results/{trader.trading_mechanism.fast_length}_{trader.trading_mechanism.slow_length}_{trader.stop_loss_percent}_{trader.trailing_loss_percent}_{trader.take_profit_percent}/made_trades.png")

def plot_equity(trader):
    fig = plt.figure()
    ax = fig.add_subplot()
    trader.wallet.data["Equity"].plot(ax=ax, title="Equity curve resulting from trades", xlabel="Date", ylabel="Equity")
    # plt.savefig(f"results/{trader.trading_mechanism.fast_length}_{trader.trading_mechanism.slow_length}_{trader.stop_loss_percent}_{trader.trailing_loss_percent}_{trader.take_profit_percent}/equity_curve.png")
    return fig

def plot_drawdown(trader):
    fig = plt.figure()
    ax = fig.add_subplot()
    trader.wallet.data["Drawdown"].plot.area(ax=ax, title="Maximum Drawdown of equity", xlabel="Date", ylabel="Percentage MDD", color='r')
    # plt.savefig(f"results/{trader.trading_mechanism.fast_length}_{trader.trading_mechanism.slow_length}_{trader.stop_loss_percent}_{trader.trailing_loss_percent}_{trader.take_profit_percent}/drawdown_curve.png")
    return fig

def plot_monte_carlo(mcs):
    fig = plt.figure()
    ax = fig.add_subplot()
    names = [str(i) for i in range(1, mcs.k+1)]
    mcs.alternative_equities[names].plot(ax=ax, color='k', linestyle='--', markersize=1, legend=False)
    mcs.alternative_equities["True"].plot(ax=ax, color='r', markersize=40, title="MCS of {0} possible equity curves".format(mcs.k), xlabel="Date", ylabel="Equity")
    # plt.savefig(f"results/{mcs.trader.trading_mechanism.fast_length}_{mcs.trader.trading_mechanism.slow_length}_{mcs.trader.stop_loss_percent}_{mcs.trader.trailing_loss_percent}_{mcs.trader.take_profit_percent}/mcs.png")
    return fig

def plot_mae(trader):
    fig = plt.figure()
    ax = fig.add_subplot()
    drawdowns = [abs(trade.mdd) for trade in trader.past_trades]
    data = [[abs(trade.mdd), trade.pl, abs(trade.pl)] for trade in trader.past_trades]
    trades_mae = pd.DataFrame(data=data, index=drawdowns, columns=["Drawdown", "PL", "P/L"])
    ax.set_ybound(lower=0)
    ax.set_xbound(lower=0)
    trades_mae[trades_mae["PL"] > 0].plot.scatter(title="Maximum Adverse Excursion", x="Drawdown", y="P/L", ax=ax, color='g', marker='^')
    trades_mae[trades_mae["PL"] <= 0].plot.scatter(title="Maximum Adverse Excursion", x="Drawdown", y="P/L", ax=ax, color='r', marker='v')
    return fig

def plot_mfe(trader):
    fig = plt.figure()
    ax = fig.add_subplot()
    drawdowns = [trade.mru for trade in trader.past_trades]
    data = [[trade.mru, trade.pl, abs(trade.pl)] for trade in trader.past_trades]
    trades_mae = pd.DataFrame(data=data, index=drawdowns, columns=["Runup", "PL", "P/L"])
    ax.set_ybound(lower=0)
    ax.set_xbound(lower=0)
    trades_mae[trades_mae["PL"] > 0].plot.scatter(title="Maximum Favourable Excursion", x="Runup", y="P/L", ax=ax, color='g', marker='^')
    trades_mae[trades_mae["PL"] <= 0].plot.scatter(title="Maximum Favourable Excursion", x="Runup", y="P/L", ax=ax, color='r', marker='v')
    return fig
    