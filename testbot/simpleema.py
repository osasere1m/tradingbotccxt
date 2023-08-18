import ccxt
import pandas as pd
import time
import schedule


# create exchange object
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
})

exchange.set_sandbox_mode(True) # activates testnet mode

# set symbol, leverage, position size, and time frame
symbol = 'DOGE/USDT'

timeframe = '1h'

def ask():
    ticker = exchange.fetch_ticker(symbol)
    return ticker['ask']

def bid():
    ticker = exchange.fetch_ticker(symbol)
    return ticker['bid']

def check_ema_crossover():
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    ema1 = df['close'].ewm(span=10, adjust=False).mean()
    ema2 = df['close'].ewm(span=30, adjust=False).mean()
    ema3 = df['close'].ewm(span=50, adjust=False).mean()

    if ema3.iloc[-1] > ema1.iloc[-1] and ema3.iloc[-2] < ema1.iloc[-2] and ema3.iloc[-1] > ema2.iloc[-1] and ema3.iloc[-2] < ema2.iloc[-2]:
        # EMA 3 crossed above EMA 1 and EMA 2, place a long order
        price = ask()
        order = exchange.create_order(symbol, type='limit', side='buy', amount=position_size, price=price, params={"leverage": leverage})
        print(f"Placed long order: {order}")

    elif ema3.iloc[-1] < ema1.iloc[-1] and ema3.iloc[-2] > ema1.iloc[-2] and ema3.iloc[-1] < ema2.iloc[-1] and ema3.iloc[-2] > ema2.iloc[-2]:
        # EMA 3 crossed below EMA 1 and EMA 2, place a short order
        price = bid()
        order = exchange.create_order(symbol, type='limit', side='sell', amount=position_size, price=price, params={"leverage": leverage})
        print(f"Placed short order: {order}")

schedule.every(2).minutes.do(check_ema_crossover)

while True:
    schedule.run_pending()
    time.sleep(1)
