import ccxt
#Here's an example of a function that creates a short or long order with a market type when there is no open position:
def create_order(exchange, symbol, order_type):
    open_positions = exchange.fetch_open_orders(symbol)
    
    if len(open_positions) == None:
        if order_type == "short":
            # Place a market order for a short position
            order = exchange.create_order(symbol, type='market', side='sell', amount=1)
            print("Short order created.")
        elif order_type == "long":
            # Place a market order for a long position
            order = exchange.create_order(symbol, type='market', side='buy', amount=1)
            print("Long order created.")
        else:
            print("Invalid order type.")
    else:
        print("There is already an open position.")

# Usage example:
exchange = ccxt.bybit()  # Replace with your exchange instance
symbol = 'LTC/USDT'  # Replace with your desired trading pair
order_type = 'short'  # Replace with 'long' for a long position

create_order(exchange, symbol, order_type)

#Here's the modified code that includes a trailing stop after the position's entryprice has increased by 2%:
def kill_switch():
    positions = bybit.fetch_positions()
    print(f"{positions}information")
    for position in positions:
        if abs(position['contracts']) > 0:
            ids = position['id']
            symbol = position['symbol']
            entryPrice = position['entryPrice']
            amount = position['contracts']
            
            type = 'limit'
            price = orderbook['asks'][0][0]
            
            print(f"{symbol} and {entryPrice}, {amount}")
            
            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
            
            print(f"{pnl} percent")
            
            if pnl <= -10 or pnl >= 20:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                if position['side'] == 'short':
                    side = 'buy'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, ask)
                    if order:
                        print(f"Position closed: {order}")
                else:
                    side = 'sell'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, ask)
                    if order:
                        print(f"Position closed: {order}")
            elif pnl >= 2:
                print(f"Setting trailing stop for {symbol} at 2% profit")
                
                if position['side'] == 'short':
                    side = 'buy'
                    stop_price = entryPrice * 1.02  # 2% above entry price
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, stop_price)
                    if order:
                        print(f"Trailing stop set: {order}")
                else:
                    side = 'sell'
                    stop_price = entryPrice * 0.98  # 2% below entry price
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, stop_price)
                    if order:
                        print(f"Trailing stop set: {order}")


# Run the kill switch function
kill_switch()








#Here's the modified code that includes a trailing stop after the position's current price has increased by 2%:


def kill_switch():
    positions = bybit.fetch_positions()
    print(f"{positions}information")
    for position in positions:
        if abs(position['contracts']) > 0:
            ids = position['id']
            symbol = position['symbol']
            entryPrice = position['entryPrice']
            amount = position['contracts']
            
            type = 'limit'
            ob = exchange.fetch_or
            price = orderbook['asks'][0][0]
            
            print(f"{symbol} and {entryPrice}, {amount}")
            
            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
            
            print(f"{pnl} percent")
            
            if pnl <= -10 or pnl >= 20:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                if position['side'] == 'short':
                    side = 'buy'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, ask)
                    if order:
                        print(f"Position closed: {order}")
                else:
                    side = 'sell'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, ask)
                    if order:
                        print(f"Position closed: {order}")
            elif pnl >= 2:
                print(f"Setting trailing stop for {symbol} at 2% profit")
                
                current_price = orderbook['bids'][0][0]  # Assuming current price is available in the orderbook
                if position['side'] == 'short':
                    side = 'buy'
                    stop_price = current_price * 1.02  # 2% above current price
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, stop_price)
                    if order:
                        print(f"Trailing stop set: {order}")
                else:
                    side = 'sell'
                    stop_price = current_price * 0.98  # 2% below current price
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, stop_price)
                    if order:
                        print(f"Trailing stop set: {order}")


# Run the kill switch function
kill_switch()


#kucoin market scanner
#ideas 
import ccxt
import pandas as pd
import schedule
import time

# Initialize KuCoin client
exchange = ccxt.kucoin()

# List to store tokens to buy
tokens_to_buy = []

# Scanning logic
def scan_market():
    # Fetch all tickers
    markets = exchange.load_markets()
    tickers = exchange.fetch_tickers()

    # Clear previous tokens to buy
    tokens_to_buy.clear()
    

    # Scanning logic
    for symbol, ticker in tickers.items():
        if symbol.endswith('/USDT'):  # Filter for USDT pairs
            close_price = ticker['close']
            ema_20 = ticker['info']['ema20']
            ema_50 = ticker['info']['ema50']
            adx_14 = ticker['info']['adx14']

            if (close_price > ema_50) and (close_price < ema_20) and (ema_20 < ema_50) and (adx_14 > 25) and (close_price <= 1):
                tokens_to_buy.append(symbol)

    # Save tokens to buy to a CSV file
    df = pd.DataFrame(tokens_to_buy, columns=['Tokens'])
    print(df)
    df.to_csv('tokens_to_buy.csv', index=False)

    print("Tokens to buy saved to tokens_to_buy.csv")

# Schedule the scanning logic to run every 10 minutes
schedule.every(10).minutes.do(scan_market)

# Run the scanning logic immediately
scan_market()

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
