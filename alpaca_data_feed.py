import alpaca_trade_api as tradeapi
from datetime import datetime

# Make sure to replace these with your own API key and secret
API_KEY = 'PKKNHFMBYL0ZANV5NGQG'
API_SECRET = 'U0j16zJLNetvVqcsbMjnMtvYRwaIvqEIUxbM32YI'
BASE_URL = 'https://paper-api.alpaca.markets'

class AlpacaDataFeed:
    def __init__(self):
        self.api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

    def get_latest_market_data(self, symbol, timeframe='1Min', limit=1):
        """
        Get the latest market data for the specified symbol and timeframe.
        
        Args:
            symbol (str): The stock symbol.
            timeframe (str): The timeframe for the market data (default: '1Min').
            limit (int): The number of data points to return (default: 1).
        
        Returns:
            pandas.DataFrame: A DataFrame containing the latest market data.
        """
        market_data = self.api.get_barset(symbol, timeframe, limit=limit).df[symbol]
        market_data.index = market_data.index.tz_convert('US/Eastern')
        return market_data

    def get_historical_data(self, symbol, start_date, end_date=None, timeframe='1Min'):
        """
        Get historical market data for the specified symbol, date range, and timeframe.
        
        Args:
            symbol (str): The stock symbol.
            start_date (datetime.date): The start date for the historical data.
            end_date (datetime.date): The end date for the historical data (default: None).
            timeframe (str): The timeframe for the market data (default: '1Min').
        
        Returns:
            pandas.DataFrame: A DataFrame containing the historical market data.
        """
        if end_date is None:
            end_date = datetime.now().date()

        market_data = self.api.get_barset(
            symbol, timeframe, start=start_date.isoformat(), end=end_date.isoformat()
        ).df[symbol]
        market_data.index = market_data.index.tz_convert('US/Eastern')
        return market_data
