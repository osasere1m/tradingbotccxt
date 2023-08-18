import ccxt
import pandas as pd
import time
import talib

# Define Supertrend function
def supertrend(high, low, close, length=10, multiplier=3):
    hl2 = (high + low) / 2.0
    atr = talib.ATR(high, low, close, timeperiod=length)
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    trend = []
    long_trend = False
    for i in range(len(close)):
        if close[i] > upperband[i]:
            if not long_trend:
                trend.append(1)
                long_trend = True
            else:
                trend.append(1)
        elif close[i] < lowerband[i]:
            if long_trend:
                trend.append(-1)
                long_trend = False
            else:
                trend.append(-1)
        else:
            trend.append(0)
    return trend

# Define Madrid Moving Average Ribbon function
def madrid_ribbon(close, fast_length=5, slow_length=10, very_slow_length=20):
    fast_ma = talib.SMA(close, timeperiod=fast_length)
    slow_ma = talib.SMA(close, timeperiod=slow_length)
    very_slow_ma = talib.SMA(close, timeperiod=very_slow_length)
    ribbon = []
    for i in range(len(close)):
        if close[i] > fast_ma[i] and close[i] > slow_ma[i] and close[i] > very_slow_ma[i]:
            ribbon.append(1)
        elif close[i] < fast_ma[i] and close[i] < slow_ma[i] and close[i] < very_slow_ma[i]:
            ribbon.append(-1)
        else:
            ribbon.append(0)
    return ribbon

# Define Binance API credentials
api_key = 'YOUR_API_KEY'
secret_key = 'YOUR_SECRET_KEY'

# Initialize Binance exchange object
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
})

# Define trading parameters
symbol = 'DOGE/USDT'
leverage = 10
position_size = 10

# Load market data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe='5m')
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Calculate Supertrend and Madrid Ribbon indicators
df['supertrend'] = supertrend(df['high'], df['low'], df['close'])
df['madrid_ribbon'] = madrid_ribbon(df['close'])

# Place orders based on Supertrend and Madrid Ribbon signals
for i in range(1, len(df)):
    # Long signal
    if df['supertrend'][i] == 1 and df['supertrend'][i-1] == 0 and all(x == 1 for x in df['madrid_ribbon'][i-1:i+1]):
        order_price = df['close'][i]
        stop_loss = df['supertrend'][i] * supertrend(df['high'][:i], df['low'][:i], df['close'][:i])[-1] # Use previous Supertrend value as stop loss
        
        take_profit = order_price + 1.5 * abs(order_price - stop_loss)
        exchange.create_order(symbol=symbol, type='LIMIT', side='BUY', amount=position_size, price=order_price, params={'leverage': leverage, 'stopPrice': stop_loss, 'timeInForce': 'GTC', 'takeProfit': take_profit})
        print(f'{df.index[i]} - Buy order placed at {order_price}')

    # Short signal
    elif df['supertrend'][i] == -1 and df['supertrend'][i-1] == 0 and all(x == -1 for x in df['madrid_ribbon'][i-1:i+1]):
        order_price = df['close'][i]
        stop_loss = df['supertrend'][i] * supertrend(df['high'][:i], df['low'][:i], df['close'][:i])[-1] # Use previous Supertrend value as stop loss
        take_profit = order_price - 1.5 * abs(order_price - stop_loss)
        exchange.create_order(symbol=symbol, type='LIMIT', side='SELL', amount=position_size, price=order_price, params={'leverage': leverage, 'stopPrice': stop_loss, 'timeInForce': 'GTC', 'takeProfit': take_profit})
        print(f'{df.index[i]} - Sell order placed at {order_price}')

time.sleep(10) # Wait for 10 seconds before checking for new signals

