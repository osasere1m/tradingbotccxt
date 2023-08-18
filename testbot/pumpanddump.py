import ccxt
import pandas as pd
import pandas_ta as ta
import time

# Initialize the KuCoin client
"""""
kucoin = ccxt.kucoin({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
})


kucoin = ccxt.kucoin()

# Fetch ticker data
tickers = kucoin.fetch_tickers()
time.sleep(20)

# Prepare the data
data = []
for symbol, ticker in tickers.items():
    if 'close' in ticker:
        data.append({'symbol': symbol, 'close': ticker['close']})

df = pd.DataFrame(data)

# Define a function to check if the ticker should be filtered out
def should_filter(symbol):
    #endings = [' UNI3L', 'ARPAUP', 'ALGODOWN' 'ARB3L', '2L', 'DOWN']
    #endings = ['USDT']
    endings = ['BTC', 'KCS', 'USDC' 'DAI']


    return any(symbol.endswith(ending) for ending in endings)

# Filter out tickers with specified endings
df = df[~df['symbol'].apply(should_filter)]

# Calculate the 200 EMA and 100 SMA
df['200_ema'] = df['close'].ewm(span=200).mean()
df['100_ema'] = df['close'].ewm(span=100).mean()
df['50_ema'] = df['close'].ewm(span=50).mean()
df['20_ema'] = df['close'].ewm(span=20).mean()

print(df)

# Filter the DataFrame
filtered_df = df[(df['close'] < df['200_ema']) & (df['close'] < df['50_ema']) &  (df['close'] > df['20_ema'])]

print(filtered_df)

"""""
import ccxt
import pandas as pd
import time

# Initialize the KuCoin client
"""""
kucoin = ccxt.kucoin({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
})
"""

kucoin = ccxt.kucoin()

# Fetch ticker data
tickers = kucoin.fetch_tickers()
time.sleep(20)

# Prepare the data
data = []
for symbol, ticker in tickers.items():
    if 'close' in ticker:
        data.append({'symbol': symbol, 'close': ticker['close']})

df = pd.DataFrame(data)

# Define a function to check if the symbol should be removed
def should_remove(symbol):
    endings = ['3S', '3L', 'UP', '2L', 'DOWN']
    return any(symbol.endswith(ending) for ending in endings)

# Remove symbols with specified endings
df = df[~df['symbol'].apply(should_remove)]

# Get historical data and calculate EMAs for each ticker
ema_periods = [200, 50, 20]
for symbol in df['symbol']:
    try:
        historical_data = kucoin.fetch_ohlcv(symbol, timeframe='1h', since=None, limit=max(ema_periods))
        if len(historical_data) >= max(ema_periods):
            historical_df = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'], unit='ms')
            historical_df.set_index('timestamp', inplace=True)

            for ema_period in ema_periods:
                ema_column = f'ema_{ema_period}'
                historical_df[ema_column] = historical_df['close'].ewm(span=ema_period, min_periods=ema_period).mean()

            # Filter the DataFrame based on the specified conditions
            filtered_df = historical_df[(historical_df['close'] > historical_df['ema_200']) &
                                        (historical_df['close'] > historical_df['ema_50']) &
                                        (historical_df['close'] < historical_df['ema_20'])]
                                        

            if not filtered_df.empty:
                print(f"Filtered DataFrame for {symbol}:\n{filtered_df[['close', 'ema_200', 'ema_50', 'ema_20']].tail()}\n")
            else:
                print(f"{symbol} does not meet the filtering conditions.\n")
        else:
            print(f"Not enough historical data available for {symbol} to calculate EMAs.\n")
    except ccxt.BaseError as e:
        print(f"Error fetching historical data for {symbol}: {e}\n")

# Note: You might need to adjust the EMA periods (ema_periods) as needed.
