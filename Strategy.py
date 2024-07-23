import pandas as pd
# pass the data fetched from AlpacaDataFeed to the MovingAverageCrossoverStrategy's generate_signals method, 
#the data should be in the form of a DataFrame with a 'close' column. And it is here.
class Strategy:

    class MovingAverageCrossoverStrategy:
        def __init__(self, symbol, short_window=50, long_window=200):
            self.symbol = symbol
            self.short_window = short_window
            self.long_window = long_window

        def generate_signals(self, historical_data):
            # Calculate the moving averages
            short_mavg = historical_data['close'].rolling(window=self.short_window).mean()
            long_mavg = historical_data['close'].rolling(window=self.long_window).mean()

            # Generate buy/sell signals
            signals = (short_mavg > long_mavg).astype(int).diff().dropna()

            return signals