#write me python binance perpetual futures trading bot using ccxt, pandas as pd. for trading logic use the 20 period SMA on th e daily to determine bearish or bullish trend. if the price is below the SMA it's bearish meaning only short trade and if the price close is above SMA take long trade. for execution of the long trade calculate the 20 period SMA at the 15timeframe only when the price close to the SMA value take the trade .for short trade executiion calculate the 20 period SMA at the 15timeframe when the price close to the SMA value take the trade .

# Logic- write me python binance perpetual futures trading bot using ccxt, pandas as pd. for trading logic use the 20 period SMA on the daily to determine bearish or bullish trend. if the price is below the SMA it's bearish meaning only short trade and if the price close is above SMA take long trade. for execution of the long trade calculate the 20 period SMA at the 15timeframe only when the price close to the SMA value take the trade .for short trade executiion calculate the 20 period SMA at the 15timeframe when the price close to the SMA value take the trade.


import ccxt
import pandas as pd
import time

# Initialize Binance client
binance_client = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'enableRateLimit': True,
})

# Set leverage
binance_client.futures_change_leverage(symbol='BTCUSDT', leverage=1)

# Retrieve market data
df = pd.DataFrame(binance_client.futures_historical_klines(
    symbol='BTCUSDT',
    interval='1d',
    start_str='2021-06-01',
    end_str='2021-06-30'
))
df = df.iloc[:, :6]
df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
df['date'] = pd.to_datetime(df['date'], unit='ms')
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col])

# Calculate SMA
sma_period = 20
sma_daily = df['close'].rolling(sma_period).mean().shift(1)
sma_15min = df['close'].rolling(sma_period * 4).mean()

# Determine trend
is_bearish = df['close'] < sma_daily
is_bullish = df['close'] > sma_daily

# Execute trades
for i in range(len(df)):
    if is_bearish[i]:
        binance_client.futures_create_order(
            symbol='BTCUSDT',
            type='MARKET',
            side='SELL',
            quantity=0.001
        )
        time.sleep(60 * 15)  # wait 15 minutes before executing next trade
    elif is_bullish[i]:
        if abs(df['close'][i] - sma_15min[i]) < 10:  # close to SMA value
            binance_client.futures_create_order(
                symbol='BTCUSDT',
                type='MARKET',
                side='BUY',
                quantity=0.001
            )
            time.sleep(60 * 15)  # wait 15 minutes before executing next trade

    # Check PNL and close trades with limit order
    trades = pd.DataFrame(binance_client.futures_account_trades(
        symbol='BTCUSDT'
    ))
    trades = trades[trades['commissionAsset'] == 'USDT']
    trades['pnl'] = pd.to_numeric(trades['realizedPnl'])
    if trades['pnl'].max() >= 0.2:
        order_book = pd.DataFrame(binance_client.futures_order_book(
            symbol='BTCUSDT'
        ))
        limit_price = (pd.to_numeric(order_book['bids'][0][0]) +
                       pd.to_numeric(order_book['asks'][0][0])) / 2
        binance_client.futures_create_order(
            symbol='BTCUSDT',
            type='LIMIT',
            side='SELL' if trades['pnl'].max() > 0 else 'BUY',
            quantity=0.001,
            price=limit_price
        )
