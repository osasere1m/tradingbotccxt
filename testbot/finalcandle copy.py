import ccxt
import pandas as pd
from datetime import datetime
import schedule
import time
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
        'adjustForTimeDifference': True,
        #'enableRateLimit': True,
    }
})




#parameters
symbol = 'LTC/USDT'
timeframe = '30m'
#since = exchange.parse8601('2023-02-01T00:00:00Z')
#limit = 2000
quantity = '0.182'
#time delay
delay = 2 # seconds
#time.sleep (delay) # rate limit
    
ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    
# Convert to Pandas DataFrame and set the columns
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Set timestamp as index
df.set_index('timestamp', inplace=True)

#display the dataframe
print(df)


#Engulfing pattern signals
import random
def Revsignal1(df1):
    high = df1['high'].tolist()

    length = len(df1)
    high = list(df1['high'])
    low = list(df1['low'])
    close = list(df1['close'])
    open = list(df1['open'])
    signal = [0] * length
    bodydiff = [0] * length

    for row in range(1, length):
        bodydiff[row] = abs(open[row]-close[row])
        bodydiffmin = 0.003
        if (bodydiff[row]>bodydiffmin and bodydiff[row-1]>bodydiffmin and
            open[row-1]<close[row-1] and
            open[row]>close[row] and 
            #open[row]>=close[row-1] and close[row]<open[row-1]):
            (open[row]-close[row-1])>=+0e-5 and close[row]<open[row-1]):
            signal[row] = 1
        elif (bodydiff[row]>bodydiffmin and bodydiff[row-1]>bodydiffmin and
            open[row-1]>close[row-1] and
            open[row]<close[row] and 
            #open[row]<=close[row-1] and close[row]>open[row-1]):
            (open[row]-close[row-1])<=-0e-5 and close[row]>open[row-1]):
            signal[row] = 2
        else:
            signal[row] = 0
        #signal[row]=random.choice([0, 1, 2])
        #signal[row]=1
    return signal
df['signal1'] = Revsignal1(df)

print(df)




#load markets
def load_markets():
    #df['signal1'] = Revsignal1(df)
    
    
    # Load market data and fetch ticker
    exchange.load_markets()
    

    # Fetch account balance
    balance_info = exchange.fetch_balance()
    print(balance_info)
    #time delay
    time.sleep (10)
    usdt_balance = balance_info['total']['USDT']
    print(usdt_balance)
    time.sleep (10)
load_markets()

#check signal
def check_signals():
    try:
        #ticker = exchange.fetch_tickers()
        

        for index, row in df.iterrows():
            signal = row['signal1']

            # Use bid and ask prices instead of close price
            if signal == 1:
                price = ['bid']
                print(f"long signal found")
                

            elif signal == 2:
                price = ['ask']
                print(f"short signal found")

            else:
                print(f"checking for signal")
                time.sleep(20)


    except ccxt.base.errors.NetworkError as e:
        print(f"NetworkError: {e}")
        print("Retrying in 10 seconds...")
        time.sleep(10)
        check_signals()
        #if price is None:
            #print(f"Unable to fetch price for {symbol}")
            #continue

        # Calculate the quantity based on 10% of the account balance
        #percent = 0.1
        #quantity = calculate_quantity(usdt_balance, price, percent)

#calculate quantity
def calculate_quantity(balance, price, percent):
    amount = balance * percent
    quantity = amount / price
    return quantity

      

#placing order function
def place_order(signal, symbol, quantity, price):
    side = None
    stop_loss_percent = 0.05
    take_profit_pips = 300
    orderbook = exchange.fetch_order_book (exchange.symbols[0])
    bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None

    stop_loss_percent = 0.05
    take_profit_pips = 300
    ticker = exchange.fetch_ticker(symbol)
    
    # Fetch positions
    positions = exchange.fetch_positions()
    print(positions)
    in_position = False

    for position in positions:
        if position['symbol'] == symbol and abs(position['size']) > 0:
            in_position = True
            break

    if in_position:
        print("Already in a position. Skipping order placement.")
        return
    

    if signal == 1:
        side = 'sell'
        stop_loss_price = price * (1 + stop_loss_percent)
        take_profit_price = price - (take_profit_pips * exchange.price_to_precision(symbol, 0.1))
    elif signal == 2:
        side = 'buy'
        stop_loss_price = price * (1 - stop_loss_percent)
        take_profit_price = price + (take_profit_pips * exchange.price_to_precision(symbol, 0.1))
    else:
        return None

    order = exchange.create_order(
        symbol=symbol,
        type='limit',
        side=side,
        amount=quantity,
        price=price,
        params={
            'timeInForce': 'GTC',
            'stopPrice': stop_loss_price,
            'stopLoss': {'stopPrice': stop_loss_price},
            'takeProfit': {'stopPrice': take_profit_price},
        }
    )
    if order:
            print(f"Order placed: {order}")

    return order


#close position
def close_position(symbol, side):
    if side == 'buy':
        close_side = 'sell'
    else:
        close_side = 'buy'

    order = exchange.create_market_order(symbol=symbol, side=close_side, amount=0, reduce_only=True)
    return order

#check pnl if less -20 and greater 50 percent
def kill_switch():
    positions = exchange.fetch_positions()
    for position in positions:
        if abs(position['contracts']) > 0:
            symbol = position['symbol']
            side = position['side']

            # Calculate PnL percentage
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100

            if pnl <= -20 or pnl >= 50:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                order = close_position(symbol, side)
                if order:
                    print(f"Position closed: {order}")


# Run the kill switch function
kill_switch()


schedule.every(1).minutes.do(check_signals)

while True:
    schedule.run_pending()
    time.sleep(20)


