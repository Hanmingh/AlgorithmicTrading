from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader

class MeanReversion(Strategy):

    def initialize(self):
        self.symbol = "QQQ"  # Asset to trade
        self.window = 20  # Moving average window
        self.threshold = 0.05  # Threshold for deviation from the mean (5%)
        self.sleeptime = "1d"  # Run the strategy daily
    
    def on_trading_iteration(self):
        # Fetch historical data
        bar = self.get_historical_prices(self.symbol, self.window + 1, "day")
        historical_data = bar.df
        if len(historical_data) < self.window:
            self.log_message("Not enough data to compute moving average.")
            return

        # Calculate moving average
        moving_average = historical_data['close'].rolling(window=self.window).mean().iloc[-1]
        current_price = self.get_last_price(self.symbol)
        deviation = (current_price - moving_average) / moving_average

        # Determine current position
        current_position = self.get_position(self.symbol)

        # Generate signals
        if deviation < -self.threshold and current_position is None:
            # Price is significantly below the moving average: Buy signal
            quantity = int(self.get_cash() // current_price)
            if quantity > 0:
                order = self.create_order(self.symbol, quantity, "buy")
                self.submit_order(order)
                self.log_message(f"Bought {quantity} shares of {self.symbol} at {current_price}")
        elif deviation > self.threshold and current_position is not None:
            # Price is significantly above the moving average: Sell signal
            order = self.create_order(self.symbol, current_position.quantity, "sell")
            self.submit_order(order)
            self.log_message(f"Sold {current_position.quantity} shares of {self.symbol} at {current_price}")

if __name__ == "__main__":
    if IS_BACKTESTING:
        start = datetime(2021, 6, 1)
        end = datetime(2024, 6, 1)
        MeanReversion.backtest(
            YahooDataBacktesting,
            start,
            end
        )
    else:
        strategy = MeanReversion(broker=Alpaca)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()