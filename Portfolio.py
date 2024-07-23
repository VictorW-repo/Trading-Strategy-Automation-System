import datetime
import numpy as np
import pandas as pd
from scipy.stats import linregress
from dataAndOrder import MarketData, TradingOrder, LimitOrder, MarketOrder, StopOrder
from alpaca_execution_handler import AlpacaExecutionHandler


'''Portfolio class handles position management, stop-loss orders, 
and position sizing rules based on the available cash and risk percentage.
And this class uses the AlpacaExecutionHandler to execute orders.'''
class Portfolio:
    def __init__(self, initial_cash, api_key, secret_key, base_url):
        self.positions = {}
        self.cash = initial_cash
        self.execution_handler = AlpacaExecutionHandler(api_key, secret_key, base_url)

    def update_position(self, symbol, quantity, price):
        if symbol not in self.positions:
            self.positions[symbol] = 0
        self.positions[symbol] += quantity
        self.cash -= quantity * price

    def execute_order(self, order):
        if order.is_valid():
            self.execution_handler.execute_order(order)
        else:
            raise ValueError("Invalid order parameters.")
            
    #to create and execute stop-loss orders based on the current position and stop-loss percentage
    def stop_loss_order(self, symbol, stop_loss_percent):
        current_position = self.positions.get(symbol, 0)
        if current_position != 0:
            stop_price = self.positions[symbol] * (1 - stop_loss_percent)
            order_type = TradingOrder.SELL if current_position > 0 else TradingOrder.BUY
            stop_order = StopOrder(symbol, order_type, abs(current_position), stop_price)
            self.execute_order(stop_order)

    #to calculate position sizing based on the available cash and a risk percentage.
    def position_sizing(self, symbol, risk_percent):
        risk_amount = self.cash * risk_percent
        return int(risk_amount / self.positions[symbol])
    
        
    def calculate_cvar(self, historical_data, confidence_level=0.95, window=252):
        """
        Calculate the Conditional Value at Risk (CVaR) for the portfolio.
        
        Args:
            historical_data (dict): A dictionary containing historical market data for each symbol in the portfolio.
                The keys should be the symbols, and the values should be Pandas DataFrame objects containing the
                historical price data.
            confidence_level (float): The confidence level for the CVaR calculation (default: 0.95).
            window (int): The window size for the historical data to be used in the calculation (default: 252).
        
        Returns:
            float: The CVaR value for the portfolio.
        """
        # Calculate the daily returns for each symbol in the portfolio
        daily_returns = {
            symbol: data['close'].pct_change().tail(window) for symbol, data in historical_data.items()
        }

        # Calculate the weighted returns for each position in the portfolio
        weighted_returns = []
        for symbol, position in self.positions.items():
            if position != 0 and symbol in daily_returns:
                symbol_returns = daily_returns[symbol] * position
                weighted_returns.append(symbol_returns)

         # Calculate the total daily returns for the portfolio
        total_returns = pd.concat(weighted_returns, axis=1).sum(axis=1)

        # Calculate the CVaR value for the specified confidence level
        var = np.percentile(total_returns, 100 * (1 - confidence_level))
        cvar = total_returns[total_returns < var].mean()

        return -cvar
