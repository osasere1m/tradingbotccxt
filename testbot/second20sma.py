import ccxt
import pandas as pd
import time

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
})

symbol = 'BTC/USDT'
daily_interval = '1d'
fifteen_min_interval = '15m'

def get_sma(interval, period):
    historical_data = exchange.fetch_ohlcv(symbol, interval)
    df = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    sma = df['close'].rolling(window=period).mean().iloc[-1]
    return sma

def execute_trade(direction):
    price = exchange.fetch_ticker(symbol)['close']
    limit_price = price * 1.01 if direction == 'buy' else price * 0.99

    order = exchange.create_order(
        symbol=symbol,
        side=direction,
        type='limit',
        price=limit_price,
        amount=0.001,
        params={'timeInForce': 'GTC'}
    )
    print(f"Order executed: {direction} 0.001 BTC at limit price {limit_price}")

while True:
    daily_sma = get_sma(daily_interval, 20)
    price = exchange.fetch_ticker(symbol)['close']
    trend = 'bullish' if price > daily_sma else 'bearish'

    fifteen_min_sma = get_sma(fifteen_min_interval, 20)
    if trend == 'bullish' and price >= fifteen_min_sma:
        execute_trade('buy')
    elif trend == 'bearish' and price <= fifteen_min_sma:
        execute_trade('sell')

    time.sleep(60 * 15)  # Wait for 15 minutes before checking again

