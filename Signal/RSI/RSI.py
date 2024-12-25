from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.credentials import IS_BACKTESTING
from lumibot.strategies import Strategy
from lumibot.traders import Trader

class RSI(Strategy):

    def initialize(self):
        self.symbol = "QQQ"  # Asset to trade
        self.rsi_period = 14  # RSI calculation period
        self.overbought = 70  # RSI overbought threshold
        self.oversold = 30  # RSI oversold threshold
        self.sleeptime = "1d"
    
    def on_trading_iteration(self):
        # Fetch historical data
        Bar = self.get_historical_prices(self.symbol, self.rsi_period + 1, "day")
        historical_data = Bar.df
        if len(historical_data) < self.rsi_period:
            self.log_message("Not enough data to compute RSI.")
            return

        # Calculate RSI
        delta = historical_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # Determine current position
        current_position = self.get_position(self.symbol)
        current_price = self.get_last_price(self.symbol)

        # Generate signals
        if rsi < self.oversold and current_position is None:
            # Buy signal
            quantity = int(self.get_cash() // current_price)
            if quantity > 0:
                order = self.create_order(self.symbol, quantity, "buy")
                self.submit_order(order)
                self.log_message(f"Bought {quantity} shares of {self.symbol} at {current_price}")
        elif rsi > self.overbought and current_position is not None:
            # Sell signal
            order = self.create_order(self.symbol, current_position.quantity, "sell")
            self.submit_order(order)
            self.log_message(f"Sold {current_position.quantity} shares of {self.symbol} at {current_price}")

if __name__ == "__main__":
    if IS_BACKTESTING:
        start = datetime(2021, 6, 1)
        end = datetime(2024, 6, 1)
        RSI.backtest(
            YahooDataBacktesting,
            start,
            end
        )
    else:
        strategy = RSI(broker=Alpaca)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()