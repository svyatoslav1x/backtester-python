import queue
import time
from datetime import datetime

import config
from tqdm import tqdm  # Import tqdm

from data import DataSource, HistoricCSVDataHandler, QuandlDataHandler
from event import FillEvent, MarketEvent, OrderEvent, SignalEvent
from execution import SimulateExecutionHandler
from portfolio import NaivePortfolio
from strategies.divide_conquer import DivideAndConquerStrategy
from strategies.hold import BuyAndHoldStrategy, SellAndHoldStrategy
from strategies.macd import (
    MovingAveragesLongShortStrategy,
    MovingAveragesLongStrategy,
    MovingAveragesMomentumStrategy,
)
from strategies.stop_loss import StopLossStrategy


def backtest(events, data, portfolio, strategy, broker):
    # Calculate total bars for the progress bar
    # We look at the first symbol in the list to determine length
    total_bars = 0
    if len(data.symbol_list) > 0:
        first_symbol = data.symbol_list[0]
        if first_symbol in data.all_data:
            total_bars = len(data.all_data[first_symbol])

    # Initialize progress bar
    with tqdm(total=total_bars, desc="Backtesting", unit="bars") as pbar:
        while True:
            data.update_latest_data()
            if not data.continue_backtest:
                break
            while True:
                try:
                    event = events.get(block=False)
                except queue.Empty:
                    break
                if event is not None:
                    if event.type == "MARKET":
                        strategy.calculate_signals(event)
                        portfolio.update_timeindex(event)
                    elif event.type == "SIGNAL":
                        portfolio.update_signal(event)
                    elif event.type == "ORDER":
                        broker.execute_order(event)
                    elif event.type == "FILL":
                        portfolio.update_fill(event)

            # Update progress bar by 1
            pbar.update(1)

    stats = portfolio.summary_stats()

    for stat in stats:
        print(stat[0] + ": " + stat[1])

    strategy.plot()
    portfolio.plot_all()


# for s in [5, 10, 50, 100, 200]:
#     for l in [s+10, s+50, s+100, s+200]:
#         events = queue.Queue()
#         data = HistoricCSVDataHandler(events, 'csv/', ['OMXS30'], DataSource.NASDAQ)
#         # data = QuandlDataHandler(events, ['OMXS30'], config.API_KEY)
#         portfolio = NaivePortfolio(data, events, '', initial_capital=2000)
#         # strategy = BuyAndHoldStrategy(data, events, portfolio)
#         # strategy = SellAndHoldStrategy(data, events, portfolio)
#         # strategy = MovingAveragesLongShortStrategy(data, events, portfolio, 100, 200, version=1)
#         # strategy = MovingAveragesMomentumStrategy(data, events, portfolio, 100, 200)
#         # strategy = StopLossStrategy(data, events, portfolio, 0.9)
#         # strategy = DivideAndConquerStrategy(data, events, portfolio)
#         strategy = MovingAveragesLongStrategy(data, events, portfolio, s, l, version=2)
#         portfolio.strategy_name = strategy.name
#         broker = SimulateExecutionHandler(events)
#         print('Short: {0}, Long: {1}'.format(s, l))
#         backtest(events, data, portfolio, strategy, broker)
#         print('----------')

events = queue.Queue()
data = HistoricCSVDataHandler(events, "csv/", ["OMXS30"], DataSource.NASDAQ)
portfolio = NaivePortfolio(data, events, "", initial_capital=2000)
strategy = MovingAveragesLongStrategy(data, events, portfolio, 50, 100, version=1)
portfolio.strategy_name = strategy.name
broker = SimulateExecutionHandler(events)

backtest(events, data, portfolio, strategy, broker)
