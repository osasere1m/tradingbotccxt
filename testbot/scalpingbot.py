from datetime import datetime
import ccxt
import numpy as np
import pandas as pd
import time



# Connect to the Bybit exchange

# Create an instance of the Bybit exchange object
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
    'options': {'defaultType': 'future'},
})

exchange.set_sandbox_mode(True) # activates testnet mode

# Get the account balance
balance = exchange.fetch_balance()

# Extract the balance of the USDT currency
account_balance = balance['total']['USDT']

symbols = exchange.load_markets()
print(symbols)

# Set the list of pairs to trade
pair = 'LTC/USDT'
timeframe = '5m'
since = exchange.parse8601('2022-01-01T00:00:00Z')
max_trade_size = 100  # or any value that you prefer

limit = 100

candles = exchange.fetch_ohlcv(pair, timeframe, since=since, limit=limit)

# Define the periods for the Madrid Moving Average Ribbon indicator
periods = [10, 20, 30, 40, 50, 60]

# Define the stop loss and take profit ratios
stop_loss_ratio = 0.01
take_profit_ratio = 0.015

# Define the leverage and risk per trade
leverage = 5
risk_per_trade = 0.1  # Use 10% of account balance per trade

#Define the function to calculate the Madrid Moving Average Ribbon
def calc_madrid_ribbon(candles):
    emas = []
    for p in periods:
        ema = pd.Series(candles[:, 4]).ewm(span=p).mean().values
        emas.append(ema)
    ribbon = np.array(emas)
    return ribbon

# Define the function to calculate the SuperTrend indicator
def calc_supertrend(candles, atr_multiplier=2, atr_period=10):
    high = candles[:, 2]
    low = candles[:, 3]
    close = candles[:, 4]
    atr = pd.Series(pd.DataFrame({
        'h-l': high - low,
        'h-pc': abs(high - close.shift(1)),
        'l-pc': abs(low - close.shift(1))
    }).max(axis=1)).ewm(span=atr_period).mean()
    hl2 = (high + low) / 2
    basic_ub = hl2 + atr_multiplier * atr
    basic_lb = hl2 - atr_multiplier * atr
    supertrend = pd.Series(0.0, index=candles[:, 0])
    supertrend[0] = np.nan
    for i in range(1, len(candles)):
        if close[i] <= basic_ub[i - 1]:
            supertrend[i] = basic_ub[i - 1]
        else:
            supertrend[i] = basic_lb[i - 1]
        if supertrend[i] < basic_ub[i]:
            supertrend[i] = basic_ub[i]
        if supertrend[i] > basic_lb[i]:
            supertrend[i] = basic_lb[i]
    return supertrend.values

# Define the function to check for buy or sell signals
def check_signals(pair):
    # Get the candles data for the specified pair and timeframe
    candles = exchange.fetch_ohlcv(pair, timeframe='5m')

    # Calculate the Madrid Moving Average Ribbon
    ribbon = calc_madrid_ribbon(candles)

    # Calculate the SuperTrend indicator
    supertrend = calc_supertrend(candles)

    # Check for buy or sell signals
    buy_signal = (ribbon[0] > ribbon[1]).all() and (ribbon[1] > ribbon[2]).all() and (ribbon[2] > ribbon[3]).all() and (ribbon[3] > ribbon[4]).all()
    if buy_signal:
        # Place long position
       # Place long position
        position_type = 'long'
        entry_price = exchange.fetch_ticker(pair)['last']
        stop_loss_price = calc_supertrend(candles)[-1]
        take_profit_price = entry_price + (entry_price - stop_loss_price) * take_profit_ratio
        quantity = min((account_balance * leverage * risk_per_trade) / entry_price, max_trade_size)
        order = exchange.create_order(pair, 'market', 'buy', quantity)
        print(f'Entered long position for {quantity} {pair} at market price {entry_price}')
        
        # Wait for the order to fill
        filled = False
        while not filled:
            # Get the order status
            order_status = exchange.fetch_order(order['id'], pair)
            if order_status['status'] == 'closed':
                filled = True
            else:
                # Wait for 5 seconds before checking the order status again
                time.sleep(5)
        # Place stop loss and take profit orders
        exchange.create_order(pair, 'stop_loss_limit', 'sell', quantity, stop_loss_price, {'stopPx': stop_loss_price})
        exchange.create_order(pair, 'take_profit_limit', 'sell', quantity, take_profit_price, {'stopPx': take_profit_price})
    

    else:
        sell_signal = (ribbon[0] < ribbon[1]).all() and (ribbon[1] < ribbon[2]).all() and (ribbon[2] < ribbon[3]).all() and (ribbon[3] < ribbon[4]).all()
        if sell_signal:
            # Place short position
            position_type = 'short'
            entry_price = exchange.fetch_ticker(pair)['last']
            stop_loss_price = calc_supertrend(candles)[-1]
            take_profit_price = entry_price - (stop_loss_price - entry_price) * take_profit_ratio
            quantity = min((account_balance * leverage * risk_per_trade) / entry_price, max_trade_size)
            order = exchange.create_order(pair, 'market', 'sell', quantity)
            print(f'Entered short position for {quantity} {pair} at market price {entry_price}')
            
            # Wait for the order to fill
            filled = False
            while not filled:
                # Get the order status
                order_status = exchange.fetch_order(order['id'], pair)
                if order_status['status'] == 'closed':
                    filled = True
                else:
                    # Wait for 5 seconds before checking the order status again
                    time.sleep(5)

            # Place stop loss and take profit orders
            exchange.create_order(pair, 'stop_loss_limit', 'buy', quantity, stop_loss_price, {'stopPx': stop_loss_price})
            exchange.create_order(pair, 'take_profit_limit', 'buy', quantity, take_profit_price, {'stopPx': take_profit_price})

def close_position(pair, position_type):
    # Get the position information
    positions = exchange.fetch_positions(pair)
    position = None
    
    for p in positions:
        if p['type'].lower() == position_type.lower():
            position = p
            break
            
    if position is None:
        print(f'No {position_type} position found for {pair}')
        return
    
    # Close the position
    quantity = abs(position['amount'])
    
    if position_type.lower() == 'long':
        order = exchange.create_order(pair, 'market', 'sell', quantity)
    else:
        order = exchange.create_order(pair, 'market', 'buy', quantity)
        
    print(f'Closed {position_type} position for {quantity} {pair} at market price {exchange.fetch_ticker(pair)["last"]}')

#Define the function to close a position
    
def check_positions(pair):
    # Get the position information
    positions = exchange.fetch_positions(pair)
    
    if len(positions) == 0:
        print(f'No open positions found for {pair}')
        return
    
    for p in positions:
        print(f'{p["type"].capitalize()} position of {abs(p["amount"])} {pair} at {p["price_avg"]}')

#Define the function to check for open positions
     
def check_positions(pair):
    # Get the position information
    positions = exchange.fetch_positions(pair)
    
    # Check if there are any open positions
    if len(positions) == 0:
        print(f'No open positions found for {pair}')
        return
    
    # Loop through each open position and print its information
    for position in positions:
        position_type = position["type"].capitalize()
        amount = abs(position["amount"])
        price_avg = position["price_avg"]
        print(f'{position_type} position of {amount} {pair} at {price_avg}')

#Define the function to check the account balance
def check_balance():
    balance = exchange.fetch_balance()
    print(f'Account balance: {balance["total"]["USDT"]}')

    #Close any open positions before starting the trading loop
    close_position(pair, 'long')
    close_position(pair, 'short')


#Start the trading loop
while True:
    try:
    # Check for buy or sell signals
        check_signals(pair)
        # Check for open positions and close them if necessary
        check_positions(pair)
        if input('Do you want to close any positions? (y/n) ') == 'y':
            position_type = input('Enter the position type to close (long/short): ')
            close_position(pair, position_type)

    # Check the account balance
    check_balance()

    # Wait for 5 minutes before checking the

while True:
# Check if there are any open positions
# ...

    buy_signal, sell_signal = check_signals(pair)
    if buy_signal:
        # Enter a long position
        

        # Exit the loop after opening a position
        break
    elif sell_signal:
        # Enter a short position
        # ...

        # Exit the loop after opening a position
        break

# Wait for 5 seconds before checking again
time.sleep(5)

     