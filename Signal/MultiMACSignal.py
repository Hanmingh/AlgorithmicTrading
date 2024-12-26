def get_macd_signal(self, symbol):
    # Define moving average windows
    classic_short_window = 10
    classic_long_window = 50
    shortterm_short_window = 5
    shortterm_long_window = 20
    midterm_short_window = 20
    midterm_long_window = 100
    longterm_short_window = 50
    longterm_long_window = 200

    # Fetch historical data
    longterm_Bar = self.get_historical_prices(asset=symbol, length=longterm_long_window + 1, timestep="day")
    longterm_data = longterm_Bar.df
    shortterm_data = longterm_data.iloc[-(shortterm_long_window+1):]
    classic_data = longterm_data.iloc[-(classic_long_window+1):]
    midterm_data = longterm_data.iloc[-(midterm_long_window+1):]

    if len(longterm_data) < longterm_long_window:
        print("Not enough data to compute long term moving averages.")
        return 0

    # Calculate long term moving averages
    longterm_short_ma = longterm_data['close'].rolling(window=longterm_short_window).mean()
    longterm_long_ma = longterm_data['close'].rolling(window=longterm_long_window).mean()
    longMACSignal = 0
    # Generate long term signals
    if longterm_short_ma.iloc[-1] > longterm_long_ma.iloc[-1] and longterm_short_ma.iloc[-2] <= longterm_long_ma.iloc[-2]:
        # Golden cross: Buy signal
        longMACSignal = 1
    elif longterm_short_ma.iloc[-1] < longterm_long_ma.iloc[-1] and longterm_short_ma.iloc[-2] >= longterm_long_ma.iloc[-2]:
        # Death cross: Sell signal
        longMACSignal = -1

    # Calculate short term moving averages
    shortterm_short_ma = shortterm_data['close'].rolling(window=shortterm_short_window).mean()
    shortterm_long_ma = shortterm_data['close'].rolling(window=shortterm_long_window).mean()
    shortMACSignal = 0
    if shortterm_short_ma.iloc[-1] > shortterm_long_ma.iloc[-1] and shortterm_short_ma.iloc[-2] <= shortterm_long_ma.iloc[-2]:
        shortMACSignal = 1
    elif shortterm_short_ma.iloc[-1] < shortterm_long_ma.iloc[-1] and shortterm_short_ma.iloc[-2] >= shortterm_long_ma.iloc[-2]:
        shortMACSignal = -1
        
    # Calculate classic moving averages
    classic_short_ma = classic_data['close'].rolling(window=classic_short_window).mean()
    classic_long_ma = classic_data['close'].rolling(window=classic_long_window).mean()
    classicMACSignal = 0
    if classic_short_ma.iloc[-1] > classic_long_ma.iloc[-1] and classic_short_ma.iloc[-2] <= classic_long_ma.iloc[-2]:
        classicMACSignal = 1
    elif classic_short_ma.iloc[-1] < classic_long_ma.iloc[-1] and classic_short_ma.iloc[-2] >= classic_long_ma.iloc[-2]:
        classicMACSignal = -1
        
    # Calculate midterm moving averages
    midterm_short_ma = midterm_data['close'].rolling(window=midterm_short_window).mean()
    midterm_long_ma = midterm_data['close'].rolling(window=midterm_long_window).mean()
    midMACSignal = 0
    if midterm_short_ma.iloc[-1] > midterm_long_ma.iloc[-1] and midterm_short_ma.iloc[-2] <= midterm_long_ma.iloc[-2]:
        midMACSignal = 1
    elif midterm_short_ma.iloc[-1] < midterm_long_ma.iloc[-1] and midterm_short_ma.iloc[-2] >= midterm_long_ma.iloc[-2]:
        midMACSignal = -1
        
    signals = [midMACSignal, shortMACSignal, longMACSignal, classicMACSignal]
    return signals