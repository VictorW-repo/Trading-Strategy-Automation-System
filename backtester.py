#backtester
# simulate the performance of different trading strategies using historical market data.
# It also incorporats stop-loss orders
import datetime
import numpy as np
import pandas as pd
from scipy.stats import linregress
from alpaca_execution_handler import AlpacaExecutionHandler
from market_data import MarketData
from alpaca_data_feed import AlpacaDataFeed
from portfolio import Portfolio
from strategy import MovingAverageCrossoverStrategy
import logging
logging.basicConfig(filename='backtester.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class Backtester:
    # __init__: a constructor that sets up the initial state of the object by initializing its attributes with default or provided values.
    def __init__(self, data_feed, strategy, initial_cash=100000, risk_percent=0.01, stop_loss_percent=0.05):
        self.data_feed = data_feed
        self.strategy = strategy
        self.portfolio = Portfolio(initial_cash)
        self.risk_percent = risk_percent
        self.stop_loss_percent = stop_loss_percent

 def run(self):
    logging.info("Backtest started")
    try:
        for market_data in self.data_feed.fetch_data():
            logging.info(f"Processing market data for {market_data['timestamp']}")

            try:
                # Generate signals from the strategy
                signal = self.strategy.generate_signal(market_data)
            except Exception as e:
                logging.error(f"Error generating signal: {str(e)}")
                continue

            if signal > 0:
                try:
                    # Calculate position size based on risk percent
                    position_size = self.portfolio.position_sizing(self.strategy.symbol, self.risk_percent)

                    # Create and execute a market order to buy
                    order = MarketOrder(self.strategy.symbol, TradingOrder.BUY, position_size, market_data['close'])
                    self.portfolio.execute_order(order, market_data)

                    # Create a stop-loss order based on the stop_loss_percent
                    self.portfolio.stop_loss_order(self.strategy.symbol, self.stop_loss_percent)

                except Exception as e:
                    logging.error(f"Error processing buy signal: {str(e)}")

            elif signal < 0:
                try:
                    # Create and execute a market order to sell the entire position
                    position_size = self.portfolio.positions.get(self.strategy.symbol, 0)
                    if position_size > 0:
                        order = MarketOrder(self.strategy.symbol, TradingOrder.SELL, position_size, market_data['close'])
                        self.portfolio.execute_order(order, market_data)

                except Exception as e:
                    logging.error(f"Error processing sell signal: {str(e)}")

        logging.info("Backtest completed")

    except Exception as e:
        logging.error(f"Error during backtest: {str(e)}")


    def evaluate_performance(self):
        # Calculate the total return and annualized return
        initial_value = self.portfolio.initial_cash
        final_value = self.portfolio.cash + sum([position * self.historical_data.iloc[-1]['close']
                                                 for symbol, position in self.portfolio.positions.items()])
        total_return = (final_value - initial_value) / initial_value
        annualized_return = (1 + total_return) ** (252 / len(self.historical_data)) - 1

        # Calculate daily returns for the portfolio
        daily_returns = self.portfolio.calculate_daily_returns(self.historical_data)

        # Calculate the Sharpe ratio
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()

        # Calculate the maximum drawdown
        drawdown = daily_returns.cumsum().cummax() - daily_returns.cumsum()
        max_drawdown = drawdown.max()

        # Calculate the Calmar ratio
        calmar_ratio = annualized_return / max_drawdown

        # Calculate the alpha and beta
        benchmark_returns = self.historical_data['close'].pct_change().dropna()
        slope, intercept, _, _, _ = linregress(benchmark_returns.values, daily_returns.values)
        alpha, beta = intercept * np.sqrt(252), slope

        # Compile the performance metrics into a dictionary
        performance_metrics = {
            'Total Return': total_return
