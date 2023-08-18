import ccxt
import ta
import pandas as pd
import time
import talib


#This bot fetches the last 1000 1-day candles for the BTC/USDT symbol on the Bybit exchange, converts them to Heikin-Ashi candles, and calculates the 20-day and 50-day exponential moving averages (EMAs) and the 14-day relative strength index (RSI). If the EMA20 is above the EMA50 and the RSI is above 50, the bot executes a buy order for 10% of the


# Define exchange and symbol
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
})

exchange.set_sandbox_mode(True) # activates testnet mode


symbol = 'LTC/USDT'

# Define Heikin-Ashi function
def heikin_ashi(data):
    ha_close = (data['open'] + data['high'] + data['low'] + data['close']) / 4
    ha_open = (ha_close.shift(1) + ha_close.shift(1)) / 2
    ha_high = data[['high', 'open', 'close']].max(axis=1)
    ha_low = data[['low', 'open', 'close']].min(axis=1)
    ha_data = data.assign(open=ha_open, high=ha_high, low=ha_low, close=ha_close)
    return ha_data

# Import talib

# Define bot function
def trading_bot(exchange, symbol):
    # Set up the bot
    balance = exchange.fetch_balance()['USDT']['free']
    while True:
        try:
            # Fetch the last 1000 candles
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=1000)
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            ha_data = heikin_ashi(data)

            # Calculate the indicators
            ha_data['ema20'] = ta.EMA(ha_data['close'].values, timeperiod=20)
            ha_data['ema50'] = ta.EMA(ha_data['close'].values, timeperiod=50)
            ha_data['rsi'] = ta.RSI(ha_data['close'].values, timeperiod=14)
            
            # Determine the trade signal
            if ha_data['ema20'][-1] > ha_data['ema50'][-1] and ha_data['rsi'][-1] > 50:
                # Buy signal
                amount = balance * 0.1 / ha_data['close'][-1]
                order = exchange.create_order(symbol, type='market', side='buy', amount=amount)
                print('Buy order executed:', order)
                balance -= order['cost']
            elif ha_data['ema20'][-1] < ha_data['ema50'][-1] and ha_data['rsi'][-1] < 50:
                # Sell signal
                amount = balance * 0.1 / ha_data['close'][-1]
                order = exchange.create_order(symbol, type='market', side='sell', amount=amount)
                print('Sell order executed:', order)
                balance += order['cost']
            
            # Wait for 24 hours before checking again
            time.sleep(86400)
            
        except Exception as e:
            print('Error:', e)
            time.sleep(60)

# Run the bot
trading_bot(exchange, symbol)
