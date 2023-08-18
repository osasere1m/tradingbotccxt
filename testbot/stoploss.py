
import ccxt
import os
import time
import schedule
import json
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')



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

symbol = 'LTC/USDT'
amount = 0.06 #size
limit = 200
#bid =
ask = 88.35
# the bid is the price, to get the bid uses fetch orderbook 
orderbook = bybit.fetch_l2_order_book(symbol, limit)
print(orderbook)
#to get bid 
bid = orderbook['bids'][0][0]
#to get the bid quantity
bid_quantity = orderbook['bids'][0][-1]
print(f" This is the current bid {bid} and quantity {bid_quantity}")
#to get ask 
asks = orderbook['asks'][0][0]
#to get the bid quantity
asks_quantity = orderbook['asks'][0][-1]
print(f" This is the current ask {asks} and quantity {asks_quantity}")

#bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
#ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None


#example for short step
#make a sell order
def sell_order():
    symbol = 'LTC/USDT'
    amount = 0.2 #size
    
    price = orderbook['bids'][0][0]
    side= 'sell'
    type = 'limit'
    

    #order = bybit.create_contract_v3_order(symbol, type, side, amount, price)
    #order = bybit.create_order(symbol, type, side, amount, ask)

    #print(order)
    #time.sleep(23)
    #stop = bybit.create_contract_v3_order(symbol, side='sell', amount='0.2', params=params)
    #print(stop)
    #stop_price = (ask * 10000) + 20000 # reason for using 10000 to multipy the bid it because of the priceEp in the sl_params
    #stop_trigger = stop_price + 20000

    params = {
        
        
        'timeInForce': 'PO',
        
    
    
    }
sell_order()

#stop_price = (ask * 10000) + 20000 # reason for using 10000 to multipy the bid it because of the priceEp in the sl_params
#stop_trigger = stop_price + 20000


"""""
sl_params = {
    'clOrdID': 'stop-loss-order-then-limit',
    'timeInForce': 'PO',
    'symbol': 'LTC/USDT',
    'side': 'buy',
    'ordType': 'StopLimit',
    'triggerType': 'ByLastPrice',
    'stopPxEp': stop_trigger,
    'priceEp': stop_price,
    'orderQty': '0.06' 
}
params = {
    
    'stopLoss': {
        'type': 'limit', # or 'market'
        'price': stop_trigger,
        'stopLossPrice': stop_price,
    }
}
"""
type = 'limit'  # or 'market'
side = 'buy'
price = 85.45
#make stoploss
time.sleep(20)
#stop = bybit.create_order(symbol, type='limit', side='buy', amount=amount, price=stop_price, params=sl_params)

#stop = exchange.create_order(symbol, type, side, amount, price, params)



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
            price = orderbook['asks'][0][0]
            
            print(f"{symbol} and {entryPrice}, {amount}")
            # Check if position has valid values for unrealizedPnl and initialMargin
            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            # Calculate PnL percentage
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
            
            print(f"{pnl} percent")
            #price less than -2% and greater than 1%
            if pnl <= -10 or pnl >= 20:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                
                if position['side'] =='short':
                    side = 'buy'
                    #order= bybit.cancel_derivatives_order(ids, symbol)
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, ask)
                    if order:
                        print(f"Position closed: {order}")
                else :
                    side = 'sell'
                    order = bybit.create_contract_v3_order(symbol, type, side, amount, ask)
                    if order:
                        print(f"Position closed: {order}")


# Run the kill switch function
kill_switch()
schedule.every(1).minutes.do(kill_switch)

while True:
    schedule.run_pending()
    time.sleep(20)



#new stoploss with network features
"""""
import requests
import time

def is_cnx_active(timeout):
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

def kill_switch():
    global stop_loss
    global stop_trigger
    global amount
    global bid

    while True:
        if is_cnx_active(timeout=5):
            positions = bybit.fetch_positions()
            for position in positions:
                if abs(position['contracts']) > 0:
                    ids = position['id']
                    symbol = position['symbol']
                    entryPrice = position['entryPrice']
                    amount = position['contracts']
                    side = position['side']
                    time = 1000  # 1 second delay between retries

                    while True:
                        try:
                            if position['side'] == 'short':
                                order = bybit.create_contract_v3_order(symbol, side='sell', amount=amount)
                                print(f"Position closed: {order}")
                            else:
                                order = bybit.create_contract_v3_order(symbol, side='buy', amount=amount)
                            break
                        except requests.ConnectionError:
                            time.sleep(time)
        else:
            print("Internet connection is down, retrying in 5 seconds...")
            time.sleep(5)
"""