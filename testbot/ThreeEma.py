import time
import ccxt
import pandas as pd




exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
})

exchange.set_sandbox_mode(True) # activates testnet mode

# Set up the trading pair and timeframe

symbol = 'ALGO/USDT'
timeframe = '5m'


# Get historical OHLCV data
from_ts = exchange.parse8601('2022-07-21 00:00:00')

ohlcv = exchange.fetch_ohlcv('ALGO/USDT', '5m', since=from_ts, limit=1000)


# Convert to Pandas DataFrame and set the columns
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Set timestamp as index
df.set_index('timestamp', inplace=True)

# Calculate the 3 EMAs
ShortEMA = df.close.ewm(span=5, adjust=False).mean()
MiddleEMA = df.close.ewm(span=8, adjust=False).mean()
LongEMA = df.close.ewm(span=13, adjust=False).mean()

#Add the EMA to the data set
df['Short'] = ShortEMA
df['Middle'] = MiddleEMA
df['Long'] = LongEMA



# Define the trading strategy
def strategy(df, position):
  

    for i in range(0, len(df)):
      if position == 'none':
          if df['Long'][i] < df['Long'][1]  and df['Short'][i] > df['Middle'][i] > df['Long'][i]:
              return 'buy'
          else:
              return 'none'
      elif position == 'long':
          entry_price = float(exchange.fetch_open_orders(symbol=symbol)[0]['price'])
          stop_loss = entry_price - (entry_price - df['low'][i]) * 2
          take_profit = entry_price + (df['high'][i] - entry_price) * 2
          if df['close'][i] <= stop_loss:
              return 'sell'
          elif df['close'][i] >= take_profit:
              return 'sell'
          else:
              return 'hold'
    


# Check the strategy signal for the last candle and current position
position = 'none'
signal = strategy(df.iloc[-2:], position)
if signal == 'buy':
    # Place a long position order with leverage of 5
    order = exchange.create_order(symbol, type='limit', side='buy', amount=1, price=df['close'][i], params={"leverage": 5})
    position = 'long'
    print(order)
elif signal == 'sell':
    # Close the long position
    order = exchange.create_order(symbol, type='limit', side='sell', amount=1, price=df['close'][i])
    position = 'none'
    print(order)
else:
    # Check the current position
    open_orders = exchange.fetch_open_orders(symbol=symbol)
    if open_orders:
        position = 'long'
    else:
        position = 'none'
        
print(position)



