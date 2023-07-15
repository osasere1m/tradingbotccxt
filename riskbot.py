
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
    'test': True,  # required by Bybit
    'enableRateLimit': True,
})

bybit.set_sandbox_mode(True) # activates testnet mode
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
            #side = position['side']
            
            type = 'market'
            
            
            print(f"{symbol} and {entryPrice}, {amount}")
            # Check if position has valid values for unrealizedPnl and initialMargin
            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            # Calculate PnL percentage
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
            
            print(f"PNL {pnl} percent For {symbol}")
            #price less than -2% and greater than 1%
            if pnl <= -5 or pnl >= 9:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                if position['side'] =='short':
                    side = 'buy'
                    #order= bybit.cancel_derivatives_order(ids, symbol)
                    order = bybit.create_contract_v3_order(symbol, type, side, amount)
                    if order:
                        print(f"Position closed: {order}")
                else :
                    side = 'sell'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount)
                    if order:
                        print(f"Position closed: {order}")


# Run the kill switch function
kill_switch()
schedule.every(1).minutes.do(kill_switch)

while True:
    schedule.run_pending()
    time.sleep(20)
