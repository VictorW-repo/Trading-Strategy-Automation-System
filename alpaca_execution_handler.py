import alpaca_trade_api as tradeapi
from dataAndOrder import TradingOrder, MarketOrder, LimitOrder, StopOrder
'''This class has methods to execute and cancel orders using the Alpaca API. 
The execute_order method accepts an order object (MarketOrder, LimitOrder, or StopOrder) 
and sends the order to the Alpaca API for execution. 
The cancel_order method accepts an order ID and sends a request to cancel the order. '''

class AlpacaExecutionHandler:
        # Initializes an instance of the Alpaca REST API client.
    def __init__(self, api_key, secret_key, base_url):
        self.api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
   
    # Submits the specified order to the Alpaca API for execution.
    def execute_order(self, order):
        if isinstance(order, MarketOrder):
            order_type = 'market'
        elif isinstance(order, LimitOrder):
            order_type = 'limit'
        elif isinstance(order, StopOrder):
            order_type = 'stop'
        else:
            raise ValueError("Invalid order type")

        side = 'buy' if order.side == TradingOrder.BUY else 'sell'

        try:#handle any exceptions that may occur when submitting the order to the Alpaca API.
            self.api.submit_order(
                symbol=order.symbol,
                qty=order.quantity,
                side=side,
                type=order_type,
                time_in_force='gtc',
                limit_price=order.limit_price if order_type == 'limit' else None,
                stop_price=order.stop_price if order_type == 'stop' else None
            )
            print(f"Order executed: {side.upper()} {order.quantity} shares of {order.symbol}")
        except Exception as e:
            print(f"Error executing order: {str(e)}")

    def cancel_order(self, order_id):
        try:
            self.api.cancel_order(order_id)
            print(f"Order {order_id} canceled")
        except Exception as e:
            print(f"Error canceling order: {str(e)}")
