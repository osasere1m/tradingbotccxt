import ccxt
import pandas as pd
import ta
import matplotlib.pyplot as plt
import mplfinance as mpf



import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})
# Fetch historical data
symbol = 'LTC/USDT'
timeframe = '1d'
ohlcv = exchange.fetch_ohlcv(symbol, timeframe)

# Create a pandas DataFrame
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Calculate the 200-period EMA
df['ema200'] = ta.trend.EMAIndicator(df['close'], window=200).ema_indicator()

# Determine the trend
df['trend'] = df['close'] > df['ema200']
df.tail

# Calculate the 20-period and 50-period EMAs
df['ema20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
df['ema50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()

# Calculate the Stochastic RSI
df['stochrsi'] = ta.momentum.StochRSIIndicator(df['close']).stochrsi()
print(df)
# Define the rules for trading
df['pullback'] = (df['close'] < df['ema20']) & (df['close'] > df['ema50'])
df['extended'] = df['close'] > df['ema20'] * 1.05
df['rsi_ob'] = df['stochrsi'] > 0.8
df['hidden_div'] = (df['close'].diff(1) < 0) & (df['stochrsi'].diff(1) > 0)

# Implement the trading strategy
df['signal'] = 0
df.loc[df['pullback'] & ~df['extended'] & df['rsi_ob'] & df['hidden_div'], 'signal'] = 1
df['position'] = df['signal'].diff()
df.loc[df['position'] == -1, 'position'] = 0

# Count the number of signals
signal_count = df['signal'].sum()
print(f'Number of signals: {signal_count}')

# Plot the candlesticks with signals highlighted
mc = mpf.make_marketcolors(up='green', down='red')
s = mpf.make_mpf_style(marketcolors=mc)
ap = [mpf.make_addplot(df['signal'], type='scatter', markersize=100, marker='^', color='blue')]
mpf.plot(df, type='candle', style=s, addplot=ap, volume=False, title='LTC/USDT', ylabel='Price')


""""
# Backtest the strategy
df['returns'] = df['close'].pct_change() * df['position'].shift(1)
df['equity_curve'] = (1 + df['returns']).cumprod()

# Visualize the strategy's performance
import matplotlib.pyplot as plt
plt.plot(df['equity_curve'])
plt.plot(df['pullback'])

plt.title('Equity Curve')
plt.xlabel('Date')
plt.ylabel('Equity')
plt.show()
"""
