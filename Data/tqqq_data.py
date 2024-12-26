import yfinance as yf
import pandas as pd

# Fetch historical data for TQQQ
symbol = "TQQQ"
data = yf.download(symbol, start="2010-01-01", end="2021-5-31", progress=False)

# Define the get_macd_signal function
def add_macd_signal(data):
    # Define moving average windows
    classic_short_window = 10
    classic_long_window = 50
    shortterm_short_window = 5
    shortterm_long_window = 20
    midterm_short_window = 20
    midterm_long_window = 100
    longterm_short_window = 50
    longterm_long_window = 200

    # Calculate moving averages
    data['longterm_short_ma'] = data['Close'].rolling(window=longterm_short_window).mean()
    data['longterm_long_ma'] = data['Close'].rolling(window=longterm_long_window).mean()
    data['shortterm_short_ma'] = data['Close'].rolling(window=shortterm_short_window).mean()
    data['shortterm_long_ma'] = data['Close'].rolling(window=shortterm_long_window).mean()
    data['classic_short_ma'] = data['Close'].rolling(window=classic_short_window).mean()
    data['classic_long_ma'] = data['Close'].rolling(window=classic_long_window).mean()
    data['midterm_short_ma'] = data['Close'].rolling(window=midterm_short_window).mean()
    data['midterm_long_ma'] = data['Close'].rolling(window=midterm_long_window).mean()

    # Generate the signals
    data['longterm_signal'] = (data['longterm_short_ma'] > data['longterm_long_ma']).astype(int) - (data['longterm_short_ma'] < data['longterm_long_ma']).astype(int)
    data['shortterm_signal'] = (data['shortterm_short_ma'] > data['shortterm_long_ma']).astype(int) - (data['shortterm_short_ma'] < data['shortterm_long_ma']).astype(int)
    data['classic_signal'] = (data['classic_short_ma'] > data['classic_long_ma']).astype(int) - (data['classic_short_ma'] < data['classic_long_ma']).astype(int)
    data['midterm_signal'] = (data['midterm_short_ma'] > data['midterm_long_ma']).astype(int) - (data['midterm_short_ma'] < data['midterm_long_ma']).astype(int)

    columns_to_remove = [
        'longterm_short_ma', 'longterm_long_ma',
        'shortterm_short_ma', 'shortterm_long_ma',
        'classic_short_ma', 'classic_long_ma',
        'midterm_short_ma', 'midterm_long_ma'
    ]
    # Drop the columns from the DataFrame
    data.drop(columns=columns_to_remove, inplace=True)

# Apply the function to the data
add_macd_signal(data)

# Export the data to an Excel file
data.to_excel("Data/TQQQ_data.xlsx")