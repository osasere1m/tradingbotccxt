# risk managment 1.47 = stoploss = 0.4 multiplied by leverage(10) = 4 percent takeprofit = 0.65* 10 = 6.5
# idea for mean revision  close below ema 50 short the close or high above ema20 with stochastic greater 84 and adx below 20
#price close above ema 200 for long trade
# entry 
#idea long close above ema 50 and close or high below ema20 with stochastic greater 24 and adx above 25

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
api_key = os.getenv('BYBIT_API_KEY')
secret_key = os.getenv('BYBIT_SECRET_KEY')
"""""
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
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }

}

#bybit.set_sandbox_mode(True) # activates testnet mode
#bybit future contract enable
bybit.options["dafaultType"] = 'future'
bybit.load_markets()
market = bybit.market('LTC/USD')
response = bybit.user_post_leverage_save({
    "symbol": market['id'],  # https://github.com/ccxt/ccxt/wiki/Manual#symbols-and-market-ids
    "leverage": 10
})
print(f"{response}X leverage")
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
timeframe = '15m'
limit = 200
ohlcv = bybit.fetch_ohlcv(symbol, timeframe)

# Convert the data into a pandas DataFrame for easy manipulation
df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df.set_index('Timestamp', inplace=True)
print(df)
# Step 5: Calculate technical indicators

#df.ta.ema(length=20, append=True)
a = ta.adx(df['High'], df['Low'], df['Close'], length = 14)
df = df.join(a)
print(df)

df.ta.ema(length=20, append=True)
df.ta.ema(length=50, append=True)
df.ta.stochrsi(length=14, append=True)

print(df)
# Define the conditions mean revision for short and long trades
# Define the conditions mean revision for short and long trades
short_condition = ((df["Close"] < df["EMA_200"]) & (df["STOCHRSIk_14_14_3_3"] > 20) & (df["ADX_14"] < 20))
long_condition = ((df["Close"] > df["EMA_200"]) & (df["STOCHRSIk_14_14_3_3"] > 30) & (df["ADX_14"] < 20))



# Filter the DataFrame based on the conditions
short_trades = df.loc[short_condition]
long_trades = df.loc[long_condition]


# Step 3: Define the trading bot function

def trading_bot(df):
    positions = bybit.fetch_positions(symbols=['LTC/USDT'])
    
    if len(positions) == False:
    
        # Step 6: Implement the trading strategy
        for i, row in df.iterrows():
            
            if not short_trades.empty:
                type = 'market'
                symbol = 'LTC/USDT'
                amount = 0.1
            
            
                print(f"short signal found")
                
                
                # Place a buy limit order with stop loss and take profit orders
                order = bybit.create_contract_v3_order(symbol, type, 'buy', amount)
                
                print(f"long order placed: {order}")
                time.sleep(20)
            
                    
                # Step 7: Check for signals and execute trades
                # Check if there is an open trade position
                # If there is no open position, place a limit order to enter the trade at the current market price
                #pass
            else:
                time.sleep(30)
                print(f"checking for short signals")
                continue 
                     
    else:
        time.sleep(20)
        print("There is already an open position.")
         


        
               


# Run the trading_bot function
trading_bot(df)



schedule.every(30).seconds.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(20)

