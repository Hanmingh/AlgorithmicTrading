from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader

class MovingAverageCrossover(Strategy):

    def initialize(self):
        self.symbol = "TQQQ"  # Asset to trade
        # For short term trading, use 5-20; 10-50 is the classic one; 20-100 is mid-long term; 50-200 is long term.
        self.short_window = 40  # Short-term moving average window
        self.long_window = 100  # Long-term moving average window
        self.sleeptime = "1h"
    
    def on_trading_iteration(self):
        # Fetch historical data
        Bar = self.get_historical_prices(self.symbol, self.long_window + 1, "day")
        historical_data = Bar.df
        if len(historical_data) < self.long_window:
            self.log_message("Not enough data to compute moving averages.")
            return

        # Calculate moving averages
        short_ma = historical_data['close'].rolling(window=self.short_window).mean().iloc[-1]
        long_ma = historical_data['close'].rolling(window=self.long_window).mean().iloc[-1]

        # Determine current position
        current_position = self.get_position(self.symbol)
        current_price = self.get_last_price(self.symbol)

        # Generate signals
        if short_ma > long_ma and current_position is None:
            # Golden cross: Buy signal
            quantity = int(self.get_cash() // current_price)
            if quantity > 0:
                order = self.create_order(self.symbol, quantity, "buy")
                self.submit_order(order)
                self.log_message(f"Bought {quantity} shares of {self.symbol} at {current_price}")
        elif short_ma < long_ma and current_position is not None:
            # Death cross: Sell signal
            order = self.create_order(self.symbol, current_position.quantity, "sell")
            self.submit_order(order)
            self.log_message(f"Sold {current_position.quantity} shares of {self.symbol} at {current_price}")

if __name__ == "__main__":
    if IS_BACKTESTING:
        start = datetime(2022, 6, 1)
        end = datetime(2024, 6, 1)
        MovingAverageCrossover.backtest(
            YahooDataBacktesting,
            start,
            end
        )
    else:
        strategy = MovingAverageCrossover(broker=Alpaca)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()