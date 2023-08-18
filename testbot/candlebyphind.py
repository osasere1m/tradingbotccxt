"""
write me the code to build a Python script for analyzing candlestick patterns, confirming signals with the 200-period SMA, and executing limit orders for perpetual futures swap using the ccxt library. We will focus on identifying bullish and bearish engulfing candlestick patterns within the 1-hour timeframe for the LTC/USDT trading pair on the Binance exchange. By incorporating technical analysis indicators such as the SMA, we can enhance our trading decisions. Let's dive in!

Section 1: Setting up the Environment
1. Importing the necessary libraries: pandas as pd, pandas_ta for technical analysis, ccxt for exchange connectivity.

Section 2: Candlestick Pattern Identification
1. Fetching historical OHLCV data: Utilize the ccxt library to retrieve historical OHLCV data for the LTC/USDT trading pair on the Binance exchange, considering the 1-hour timeframe.
2. Creating a pandas DataFrame: Convert the fetched data into a pandas DataFrame for easy manipulation and analysis.
3. Identifying bullish and bearish engulfing patterns: Implement the logic to scan the candlestick data within the DataFrame for bullish and bearish engulfing patterns, comparing the current and previous candlesticks' open, high, low, and close values.

Section 3: Trend Confirmation with SMA
1. Calculating the 200-period SMA: Use pandas_ta to calculate the 200-period Simple Moving Average based on the closing prices within the DataFrame.
2. Determining the trend: Compare the current price with the 200-period SMA. If the price is below the SMA, consider it bearish and suggest short positions. If the price is above the SMA, consider it bullish and recommend long positions.

Section 4: Placing Limit Orders with Stop Loss and Take Profit
1. Connecting to the futures exchange: Set up the connection to the Binance exchange using ccxt, ensuring access to the desired perpetual futures trading pair (LTC/USDT).
2. Building a function for placing limit orders: Develop a function that takes inputs such as the symbol, side (long or short), price, stop loss percentage, and take profit percentage. Utilize the ccxt library to place limit orders accordingly, considering the provided parameters.
3. Executing the limit orders: Call the function with the appropriate parameters based on the identified candlestick patterns and confirmed trend, placing limit orders with suitable stop loss and take profit levels.
Section 5: Checking DataFrame for Signal and Placing Orders

Define a function to check the DataFrame for a signal and place an order if a signal is present:
"""
import ccxt
import pandas as pd
import pandas_ta as ta
import time
import schedule

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

# Initialize the exchange
bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
})

bybit.set_sandbox_mode(True) # activates testnet mode

def load_markets():
   
    # Load market data 
    market = bybit.load_markets()
    

    # Fetch account balance
    balance_info = bybit.fetch_balance()
    print(balance_info)
    #time delay
    time.sleep (10)
    usdt_balance = balance_info['total']['USDT']
    print(usdt_balance)
    time.sleep (10)
load_markets()

# Fetch historical OHLCV data
symbol = 'LTC/USDT'
timeframe = '1h'
ohlcv = bybit.fetch_ohlcv(symbol, timeframe)

# Create a pandas DataFrame
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
print(df)


# Identify bullish and bearish engulfing patterns
df['bullish_engulfing'] = ((df['close'].shift(1) < df['open'].shift(1)) & (df['close'] > df['open']) &
                            (df['close'] > df['close'].shift(1)) & (df['open'] < df['open'].shift(1)))
df['bearish_engulfing'] = ((df['close'].shift(1) > df['open'].shift(1)) & (df['close'] < df['open']) &
                            (df['close'] < df['close'].shift(1)) & (df['open'] > df['open'].shift(1)))

print(df)
import psutil 
 
# Start monitoring CPU usage 
cpu_start = psutil.cpu_percent() 
 
# Run some code here 
 
# Stop monitoring CPU usage 
cpu_end = psutil.cpu_percent() 
 
# Calculate the difference between the start and end points 
cpu_diff = cpu_end - cpu_start 
 
print("CPU usage:", cpu_diff, "%")
# Calculate the 200-period SMA
df.ta.sma(200, append=True)

# Determine the trend
df['trend'] = 'neutral'
df.loc[df['close'] > df['SMA_200'], 'trend'] = 'bullish'
df.loc[df['close'] < df['SMA_200'], 'trend'] = 'bearish'

print(df)
 # Load market data 


def place_order(symbol, side, price, stop_loss_pct, take_profit_pct):
    global position
    # Calculate stop loss and take profit prices
    stop_loss_price = price * (2 - stop_loss_pct / 100) if side == 'buy' else price * (2 + stop_loss_pct / 100)
    take_profit_price = price * (4 + take_profit_pct / 100) if side == 'buy' else price * (4 - take_profit_pct / 100)
    amount = 0.2
   
    
    # Check if there is already an open position
    if position is not None:
        print(f"There is already an open position: {position}")
        return None
    # Place the limit order
    order = bybit.create_order(symbol, 'limit', side, amount, price)

    # Set the stop loss and take profit orders
    if order['status'] == 'open':
        if side == 'buy':
            stop_loss = bybit.create_contract_v3_order(symbol, 'stop_loss_limit', 'sell', amount, stop_loss_price, {'stopPrice': stop_loss_price})
            take_profit = bybit.create_contract_v3_order(symbol, 'take_profit_limit', 'sell', amount, take_profit_price, {'stopPrice': take_profit_price})
        else:
            stop_loss = bybit.create_contract_v3_order(symbol, 'stop_loss_limit', 'buy', amount, stop_loss_price, {'stopPrice': stop_loss_price})
            take_profit = bybit.create_contract_v3_order(symbol, 'take_profit_limit', 'buy', amount, take_profit_price, {'stopPrice': take_profit_price})
        
        # Update the position variable
        position = {'side': side, 'price': price, 'stop_loss_price': stop_loss_price, 'take_profit_price': take_profit_price, 
                    'stop_loss_order_id': stop_loss['id'], 'take_profit_order_id': take_profit['id'], 'status': 'open'}

# Loop through each row in the DataFrame
position = None
def check_signal_and_place_order(df):
    orderbook = bybit.fetch_order_book (bybit.symbols[0])
    bid = orderbook['bids'][0][0] 
    ask = orderbook['asks'][0][0] 
    # Fetch positions
    positions = bybit.fetch_positions()
    global position

    symbol = "LTC/USDT"
    for i, row in df.iterrows():
        # Check for bullish engulfing pattern
        if row['bullish_engulfing'] and row['trend'] == 'bullish':
            print(f"long signal found")

            if position is None:
                # Place a buy limit order with stop loss and take profit orders
                order = place_order(symbol,'buy', 'bid', 2, 4)
                
                print(f"Buy order placed: {order}")
            else:
                print(f"There is already an open position: {position}")
        
        # Check for bearish engulfing pattern
        elif row['bearish_engulfing'] and row['trend'] == 'bearish':
            print(f"short signal found")
            if position is None:
                # Place a sell limit order with stop loss and take profit orders
                order = place_order(symbol,'sell', 'ask', 2, 4)
                
                print(f"Sell order placed: {order}")
            else:
                print(f"There is already an open position: {position}")

        else:
            print(f"checking for signal")
            continue
            time.sleep(20)

    # Check if the open position is filled or canceled
        if position is not None:
            symbol = "LTC/USDT"  # change for your symbol
            since = None
            limit = 20 
            orders = bybit.fetch_orders(symbol, since, limit)
            for order in orders:
                if order['id'] == position['stop_loss_order_id'] and order['status'] != 'open':
                    # Stop loss order filled or canceled
                    position['status'] = 'closed'
                    print(f"Stop loss order {order['id']} {order['status']}")
                elif order['id'] == position['take_profit_order_id'] and order['status'] != 'open':
                    # Take profit order filled or canceled
                    position['status'] = 'closed'
                    print(f"Take profit order {order['id']} {order['status']}")
            if position['status'] == 'closed':
                position = None
    
schedule.every(1).minutes.do(check_signal_and_place_order, df)

while True:
    schedule.run_pending()
    time.sleep(60)