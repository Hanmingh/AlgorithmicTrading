from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.brokers import Alpaca
from lumibot.credentials import IS_BACKTESTING
from lumibot.traders import Trader

class MultiMAC(Strategy):
    def initialize(self):
        self.symbol = "TQQQ"  # Asset to trade
        self.sleeptime = "1D"

        # Classic MAC
        self.classic_short_window = 10
        self.classic_long_window = 50

        # ShortTerm Mac
        self.shortterm_short_window = 5
        self.shortterm_long_window = 20

        # MidTerm Mac
        self.midterm_short_window = 20
        self.midterm_long_window = 100

        # LongTerm Mac
        self.longterm_short_window = 50
        self.longterm_long_window = 200
    
    def on_trading_iteration(self):
        """
        Signal of Moving Average Crossover Strategy
        """
        # Fetch historical data
        longterm_Bar = self.get_historical_prices(self.symbol, self.longterm_long_window + 1, "day")
        longterm_data = longterm_Bar.df
        shortterm_data = longterm_data.iloc[-(self.shortterm_long_window+1):]
        classic_data = longterm_data.iloc[-(self.classic_long_window+1):]
        midterm_data = longterm_data.iloc[-(self.midterm_long_window+1):]
        if len(longterm_data) < self.longterm_long_window:
            self.log_message("Not enough data to compute long term moving averages.")
            return

        # Calculate long term moving averages
        longterm_short_ma = longterm_data['close'].rolling(window=self.longterm_short_window).mean().iloc[-1]
        longterm_long_ma = longterm_data['close'].rolling(window=self.longterm_long_window).mean().iloc[-1]
        longMACSignal = 0
        # Generate long term signals
        if longterm_short_ma > longterm_long_ma:
            # Golden cross: Buy signal
            longMACSignal = 1
        elif longterm_short_ma < longterm_long_ma:
            # Death cross: Sell signal
            longMACSignal = -1
        
        # Calculate Short term moving averages
        shortterm_short_ma = shortterm_data['close'].rolling(window=self.shortterm_short_window).mean().iloc[-1]
        shortterm_long_ma = shortterm_data['close'].rolling(window=self.shortterm_long_window).mean().iloc[-1]
        shortMACSignal = 0
        if shortterm_short_ma > shortterm_long_ma:
            shortMACSignal = 1
        elif shortterm_short_ma < shortterm_long_ma:
            shortMACSignal = -1
        
        # Calculate classic moving averages
        classic_short_ma = classic_data['close'].rolling(window=self.classic_short_window).mean().iloc[-1]
        classic_long_ma = classic_data['close'].rolling(window=self.classic_long_window).mean().iloc[-1]
        classicMACSignal = 0
        if classic_short_ma > classic_long_ma:
            classicMACSignal = 1
        elif classic_short_ma < classic_long_ma:
            classicMACSignal = -1
        
        # Calculate midterm moving averages
        midterm_short_ma = midterm_data['close'].rolling(window=self.midterm_short_window).mean().iloc[-1]
        midterm_long_ma = midterm_data['close'].rolling(window=self.midterm_long_window).mean().iloc[-1]
        midMACSignal = 0
        if midterm_short_ma > midterm_long_ma:
            midMACSignal = 1
        elif midterm_short_ma < midterm_long_ma:
            midMACSignal = -1

        # Determine current position
        current_position = self.get_position(self.symbol)
        current_price = self.get_last_price(self.symbol)

        signals = [midMACSignal, shortMACSignal, longMACSignal, classicMACSignal]
        buySignal = signals.count(1)
        sellSignal = signals.count(-1)

        if buySignal > 2 and current_position is None:
            # Buy signal
            quantity = int(self.get_cash() // current_price)
            if quantity > 0:
                order = self.create_order(self.symbol, quantity, "buy")
                self.submit_order(order)
                self.log_message(f"Bought {quantity} shares of {self.symbol} at {current_price}")
        # This is stratefy with sell short.
        elif sellSignal > 0:
            if current_position is None and sellSignal > 2:
                quantity = int(self.get_cash() // current_price)
                order = self.create_order(self.symbol, quantity, "sell_short")
                self.submit_order(order)
                self.log_message(f"Shorted {quantity} shares of {self.symbol} at {current_price}")
            elif current_position is not None:
                order = self.create_order(self.symbol, current_position.quantity, "sell")
                self.submit_order(order)
                self.log_message(f"Sold {current_position.quantity} shares of {self.symbol} at {current_price}")
        """
        # This is stratefy with no sell short.
        elif sellSignal > 0 and current_position is not None:
            order = self.create_order(self.symbol, current_position.quantity, "sell")
            self.submit_order(order)
            self.log_message(f"Sold {current_position.quantity} shares of {self.symbol} at {current_price}")
        """


if __name__ == "__main__":
    if IS_BACKTESTING:
        start = datetime(2021, 6, 1)
        end = datetime(2024, 6, 1)
        MultiMAC.backtest(
            YahooDataBacktesting,
            start,
            end
        )
    else:
        strategy = MultiMAC(broker=Alpaca)
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()