
import ccxt
import os
import time
import schedule
import json
import pandas as pd
from dotenv import load_dotenv



bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }

})

#bybit.set_sandbox_mode(True) # activates testnet mode
#bybit future contract enable
bybit.options["dafaultType"] = 'future'
bybit.load_markets()
def get_balance():
    params ={'type':'swap', 'code':'USDT'}
    account = bybit.fetch_balance(params)['USDT']['total']
    print(account)
get_balance()
#stoploss


def kill_switch():
    positions = bybit.fetch_positions()
    print(f"{positions}information")
    for position in positions:
        if abs(position['contracts']) > 0:
            ids = position['id']
            symbol = position['symbol']
            entryPrice = position['entryPrice']
            amount = position['contracts']
            
            type = 'market'
            orderbook = bybit.fetch_l2_order_book(symbol)
            price = orderbook['asks'][0][0]
            
            print(f"{symbol} and {entryPrice}, {amount}")
            
            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
            
            print(f"pnl {pnl} percent")
            
            if pnl <= -5 or pnl >= 20:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                if position['side'] == 'short':
                    side = 'buy'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount)
                    if order:
                        print(f"Position closed: {order}")
                else:
                    side = 'sell'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount)
                    if order:
                        print(f"Position closed: {order}")
            elif pnl >= 5:
                print(f"Setting trailing stop for {symbol} at 5% profit")
                
                currentprice = orderbook['bids'][0][0]  # Assuming current price is available in the orderbook
                if position['side'] == 'short':
                    side = 'buy'
                    stop_price = currentprice * 0.94  # 6 below% above current price
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, stop_price)
                    if order:
                        print(f"Trailing stop set: {order}")
                else:
                    side = 'sell'
                    stop_price = currentprice * 0.94  # 6% below current price
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, stop_price)
                    if order:
                        print(f"Trailing stop set: {order}")


# Run the kill switch function
kill_switch()
schedule.every(1).minutes.do(kill_switch)

while True:
    schedule.run_pending()
    time.sleep(20)
