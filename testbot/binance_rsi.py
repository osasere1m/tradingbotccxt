#mean reversion using rsi- long only


#time sleep after a trade 10mins, risk managment 1.47 = stoploss = 0.4 multiplied by leverage(10) = 4 percent takeprofit = 0.65* 10 = 6.5 


import ccxt
import pandas as pd
import pandas_ta as ta
import time
import schedule
# Step 1: Import the necessary libraries

# Step 2: Set up the exchange connection

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

binance = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})


#binance future contract enable
#binance.options["dafaultType"] = 'future'
#binance.load_markets()
def load_markets():
   
    # Load market data 
    market = binance.load_markets()
    

    # Fetch account balance
    balance_info = binance.fetch_balance()
    #print(balance_info)
    #time delay
    time.sleep (10)
    usdt_balance = balance_info['total']['USDT']
    print(usdt_balance)
    time.sleep (10)
load_markets()



#Step 4: Fetch historical data
symbol = 'LTC/USDT'
amount = 0.1 
type = 'market'
timeframe = '5m'
limit = 200
ohlcv = binance.fetch_ohlcv(symbol, timeframe)

# Convert the data into a pandas DataFrame for easy manipulation
df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Timestamp', inplace=True)
print(df)
# Step 5: Calculate technical indicators

#df.ta.ema(length=20, append=True)
df["EMA_20"] = df['Close'].ewm(span=100).mean()
df.ta.ema(length=50, append=True)
df.ta.ema(length=200, append=True)
df.ta.rsi(length=14, append=True)
df.ta.stochrsi(length=14, append=True)
print(df)






# Step 3: Define the trading bot function


def trading_bot(df):
    positions = binance.fetch_positions()
    global position
    

    # Step 6: Implement the trading strategy
    for i, row in df.iterrows():
        amount = 0.1 
        type = 'market'
        rsi = df["RSI_14"].iloc[-1]
        print(rsi)
        
        if df["RSI_14"].iloc[-1] < 36: 
        
            print(f"long signal found")
            time.sleep(10)
            if positions is None:
                # Place a buy limit order with stop loss and take profit orders
                #order = bybit.create_contract_v3_order(symbol, type, 'buy', amount)
                order = binance.create_order(symbol, type, 'buy', amount)
                
                print(f"long order placed: {order}")
                time.sleep(20)
            else:
                print(f"There is already an open position: {positions}")
                time.sleep(20)
            # Step 7: Check for signals and execute trades
            # Check if there is an open trade position
            # If there is no open position, place a limit order to enter the trade at the current market price
            #pass
        
        else:
            time.sleep(30)
            print(f"checking for long signals")
            continue
            
    
    
    
        # Step 8: Monitor and manage open trades
      
        # Pnl check 
        positions = binance.fetch_positions()
        #print(f"{positions}information")
        for position in positions:
            if abs(position['contracts']) > 0:
                # Check if position has valid values for unrealizedPnl and initialMargin
                if position['unrealizedPnl'] is None or position['initialMargin'] is None:
                    print("Skipping position pnl due to value being zero")
                    continue
                # Calculate PnL percentage
                pnl = position['unrealizedPnl'] / position['initialMargin'] * 100
                
                print(f"{pnl} percent")

                if position['side'] =='long':
                    if positions and (df["High"].iloc[-1] > df["EMA_20"] or df["RSI_14"].iloc[-1] > 50) or (df["Close"].iloc[-1] < df["EMA_50"] and df["Close"].iloc[-1] > df["EMA_200"] and df["STOCHRSIk_14_14_3_3"] < 18 and ta.crossover(df["STOCHRSIk_14_14_3_3"],  ["STOCHRSId_14_14_3_3"])):
                        # Place a market sell order to close the trade
                        #order = bybit.create_contract_v3_order(symbol, type, 'buy', amount)
                        order = binance.create_order
                        (symbol, type, 'sell', amount)
                            
                        print(f"Exit signal order placed: {order}")
                        pass
                        time.sleep(300)

                    else:
                        pnl <= -5 or pnl >= 10
                        print(f"Closing position for {symbol} with PnL: {pnl}%")
                        side = 'sell'
                        #order = bybit.create_contract_v3_order(symbol, type, side, amount)
                        order = binance.create_order
                        (symbol, type, 'sell', amount)
                        if order:
                            print(f"Position closed: {order} with PnL: {pnl}%")
                        time.sleep(300)
                    
      



# Run the trading_bot function
trading_bot(df)



schedule.every(2).minutes.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(120)
