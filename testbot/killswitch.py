#To create a kill switch function that checks the PnL of open trades and closes the position if the PnL is -20% or +50%, you can use the fetch_positions method to get the current positions and their PnL. Then, you can create a close_position function to close the position based on the PnL. Here's the modified code:



def close_position(symbol, side):
    if side == 'buy':
        close_side = 'sell'
    else:
        close_side = 'buy'

    order = exchange.create_market_order(symbol=symbol, side=close_side, amount=0, reduce_only=True)
    return order

def kill_switch():
    positions = exchange.fetch_positions()
    for position in positions:
        if abs(position['size']) > 0:
            symbol = position['symbol']
            side = position['side']

            # Calculate PnL percentage
            pnl = position['unrealized_pnl'] / position['margin'] * 100

            if pnl <= -20 or pnl >= 50:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                order = close_position(symbol, side)
                if order:
                    print(f"Position closed: {order}")

# Run the kill switch function
kill_switch()
#for bybit
def kill_switch():
   
    positions = bybit.fetch_positions()
    print(f"{positions}")
    for position in positions:
        if abs(position['contracts']) > 0:
            symbol = position['symbol']
            side = position['side']

            # Calculate PnL percentage
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100

            print(f"{pnl}percent")
            if pnl <= -20 or pnl >= 50:
                print(f"Closing position for {symbol} with PnL: {pnl}%")
                order = bybit.create_contract_v3_order(symbol, type, side, amount)
                if order:
                    print(f"Position closed: {order}")


# Run the kill switch function
kill_switch()

#update version of kill switch 
def kill_switch():
   
    positions = bybit.fetch_positions()
    print(f"{positions}information")
    for position in positions:
        if abs(position['contracts']) > 0:
            ids = position['id']
            symbol = position['symbol']
            entryPrice = position['entryPrice']
            #side = position['side']
            amount = position['contracts']
            type = 'market'
            
            print(f"{symbol} and {entryPrice}, {amount}")
            # Check if position has valid values for unrealizedPnl and initialMargin
            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                print("Skipping position pnl due to value being zero")
                continue
            # Calculate PnL percentage
            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
            
            print(f"{pnl} percent")
            #price less than -2% and greater than 1%
            if pnl <= -2 or pnl >= 1:
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
import ccxt
exchange = ccxt.binance

#stoploss

symbol = 'LTC/USDT'
amount =1 #size
# the bid is the price, to get the bid uses fetch orderbook 
orderbook = exchange.fetch_order_book (exchange.symbols[0])
bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None

#example for short(make a sell order)
exchange.create_limit_sell_order(symbol, amount, ask)


stop_price = (bid * 10000) + 10000 # reason for using 10000 to multipy the bid it because of the priceEp in the sl_params
stop_trigger = stop_price + 20000

sl_params = {
    'clordID': 'stop-loss-order-then-limit',
    'timeInForce': 'PostOnly',
    'symbol': 'LTC/USDT',
    'side': 'Buy',#or sell
    'ordType': 'StopLimit',
    'trigger': 'ByLastPrice',
    'stopPxEp': stop_trigger,
    'priceEp': stop_price,
    'orderQty': amount 
}


stop = exchange.create_order(symbol, type='limit', side='Buy', amount=amount, price=stop_price, params=sl_params )