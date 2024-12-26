from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.brokers import Alpaca
from lumibot.credentials import IS_BACKTESTING
from lumibot.traders import Trader
from config import SLEEPTIME, SYMBOL
from Signal.MultiMACSignal import get_macd_signal

class bot(Strategy):
    def initialize(self):
        self.symbol = SYMBOL  # Asset to trade
        self.sleeptime = SLEEPTIME
    
    def on_trading_iteration(self):
        signals = get_macd_signal(self, self.symbol)

        # Determine current position
        current_position = self.get_position(self.symbol)
        current_price = self.get_last_price(self.symbol)

        buySignal = signals.count(1)
        sellSignal = signals.count(-1)

        if buySignal > 0:
            # Buy signal
            if current_position is not None and current_position.quantity < 0:
                order = self.create_order(self.symbol, -current_position.quantity, "buy_to_close")
                self.submit_order(order)
                self.log_message(f"Bought {-current_position.quantity} shares of {self.symbol} to close at {current_price}")
            elif current_position is None:
                quantity = int(self.get_cash() / current_price)
                order = self.create_order(self.symbol, quantity, "buy")
                self.submit_order(order)
                self.log_message(f"Bought {quantity} shares of {self.symbol} at {current_price}")
        # This is stratefy with sell short.
        elif sellSignal > 0:
            if current_position is None:
                quantity = int(self.get_cash() / current_price)
                order = self.create_order(self.symbol, quantity, "sell_short")
                self.submit_order(order)
                self.log_message(f"Shorted {quantity} shares of {self.symbol} at {current_price}")
            elif current_position is not None:
                order = self.create_order(self.symbol, current_position.quantity, "sell")
                self.submit_order(order)
                self.log_message(f"Sold {current_position.quantity} shares of {self.symbol} at {current_price}")


if __name__ == "__main__":
    if IS_BACKTESTING:
        start = datetime(2021, 6, 1)
        end = datetime(2024, 6, 1)
        bot.backtest(
            YahooDataBacktesting,
            start,
            end
        )
    else:
        strategy = bot(broker=Alpaca)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()