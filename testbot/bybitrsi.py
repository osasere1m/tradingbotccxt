# risk managment 1.47 = stoploss = 0.4 multiplied by leverage(10) = 4 percent takeprofit = 0.65* 10 = 6.5
# idea close below ema 50 short the close or high above ema20 with stochastic greater 70 and adx above 25
#idea long close above ema 50 and close or high below ema20 with stochastic greater 24 and adx above 25

import ccxt
import pandas as pd
import pandas_ta as ta
import time
import schedule
# Step 1: Import the necessary libraries

# Step 2: Set up the exchange connection
"""""
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})



"""""

bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,
    'test': True,  # required by Bybit

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



#Step 4: Fetch historical data
symbol = 'LTC/USDT'
amount = 0.1 
type = 'market'
timeframe = '1h'
limit = 200
ohlcv = bybit.fetch_ohlcv(symbol, timeframe)

# Convert the data into a pandas DataFrame for easy manipulation
df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Timestamp', inplace=True)
print(df)
# Step 5: Calculate technical indicators

#df.ta.ema(length=20, append=True)
df["EMA_20"] = df['Close'].ewm(span=100).mean()
df.ta.rsi(length=14, append=True)
df.ta.ema(length=20, append=True)
df.ta.ema(length=50, append=True)
df.ta.ema(length=200, append=True)
df.ta.rsi(length=14, append=True)
df.ta.stochrsi(length=14, append=True)

print(df)
# Step 3: Define the trading bot function

def trading_bot(df):
    positions = bybit.fetch_positions(symbols=['LTC/USDT'])
    
    global position
    


    # Step 6: Implement the trading strategy
    for i, row in df.iterrows():
        rsi = df["RSI_14"].iloc[-1]
        print(rsi)
        if df["RSI_14"].iloc[-1] < 50: 
        
            print(f"long signal found")
            if positions is None:
            
                # Place a buy limit order with stop loss and take profit orders
                order = bybit.create_contract_v3_order(symbol, type, 'buy', amount)
                
                print(f"long order placed: {order}")
                time.sleep(20)
            else:
                print(f"Already in position")
                
            # Step 7: Check for signals and execute trades
            # Check if there is an open trade position
            # If there is no open position, place a limit order to enter the trade at the current market price
            #pass
        
        else:
                
                if positions is True:
                    
                    # Step 8: Monitor and manage open trades
                
                    # Pnl check 
                    positions = bybit.fetch_positions()
                    #print(f"{positions}information")
                    for position in positions:
                        if abs(position['contracts']) > 0:
                            ids = position['id']
                            symbol = position['symbol']
                            entryPrice = position['entryPrice']
                            amount = position['contracts']
                            # Check if position has valid values for unrealizedPnl and initialMargin
                            if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                                print("Skipping position pnl due to value being zero")
                                continue
                            # Calculate PnL percentage
                            pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
                            print(f"The current PNL {pnl} for {symbol} and {entryPrice}, {amount}")
                            print(f"{pnl} percent")

                            #price less than -2% and greater than 1%
                            if pnl <= -5 or pnl >= 10:
                                print(f"Closing position for {symbol} with PnL: {pnl}%")
                                
                                if position['side'] =='short':
                                    side = 'buy'
                                    type = 'market'
                                    #order= bybit.cancel_derivatives_order(ids, symbol)
                                    order = bybit.create_contract_v3_order(symbol, type, side, amount)
                                    if order:
                                        print(f"Position closed: {order}")
                                        time.sleep(200)
                                else :
                                    side = 'sell'
                                    type = 'market'
                                    order = bybit.create_contract_v3_order(symbol, type, side, amount)
                                    if order:
                                        print(f"Position closed: {order}")
                                        time.sleep(200)

                else:
                    time.sleep(30)
                    print(f"checking for long signals")
                    continue      



# Run the trading_bot function
trading_bot(df)



schedule.every(2).minutes.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(40)

