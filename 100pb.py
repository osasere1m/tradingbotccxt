import ccxt
import pandas as pd
import pandas_ta as ta
import time
import schedule
# Step 1: Import the necessary libraries

# Step 2: Set up the exchange connection

bybit = ccxt.bybit({
    'apiKey': 'hqJUUDzYg1RMoQLtWq',
    'secret': 'NAquXITuPMhY3RVwGv88UsNtswn8BktrbIBA',
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
amount = 0.2 #size
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
df.ta.ema(length=200, append=True)
df.ta.ema(length=100, append=True)
df.ta.stochrsi(length=14, append=True)

print(df)
# Step 3: Define the trading bot function
def trading_bot(df):
    positions = bybit.fetch_positions()
    global position

    

    # Step 6: Implement the trading strategy
    for i, row in df.iterrows():
        if df["Close"].iloc[-1] < df["EMA_100"].iloc[-1] and df["Close"].iloc[-1] > df["EMA_200"].iloc[-1] and df["STOCHRSIk_14_14_3_3"].iloc[-1] < 0.15:
            print(f"long signal found")
            if positions is None:
                # Place a buy limit order with stop loss and take profit orders
                order = bybit.create_contract_v3_order(symbol, type, 'buy', amount)
                
                print(f"long order placed: {order}")
            else:
                print(f"There is already an open position: {positions}")
            # Step 7: Check for signals and execute trades
            # Check if there is an open trade position
            # If there is no open position, place a limit order to enter the trade at the current market price
            #pass
        elif df["Close"].iloc[-1] > df["EMA_100"].iloc[-1] and df["Close"].iloc[-1] < df["EMA_200"].iloc[-1] and df["STOCHRSIk_14_14_3_3"].iloc[-1] < 0.85:
            print(f"Short signal found")
            if positions is None:
                # Place a buy limit order with stop loss and take profit orders
                order = bybit.create_contract_v3_order(symbol, type, 'sell', amount)
                
                print(f"Short order placed: {order}")
            else:
                print(f"There is already an open position: {positions}")
        else:
            print(f"checking for signal")
            continue
            time.sleep(20)
    
    
    
        # Step 8: Monitor and manage open trades
      
        # Pnl check 
        positions = bybit.fetch_positions()
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

                if position['side'] =='short':
                    if positions and df["STOCHRSIk_14_14_3_3"].iloc[-1] > 0.85:
                        # Place a market sell order to close the trade
                        order = bybit.create_contract_v3_order(symbol, type, 'sell', amount)
                            
                        print(f"Exit signal order placed: {order}")
                    
                    else: 
                        pnl <= -5 or pnl >= 10
                        print(f"Closing position for {symbol} with PnL: {pnl}%")
                        side = 'buy'
                        #order= bybit.cancel_derivatives_order(ids, symbol)
                        order = bybit.create_contract_v3_order(symbol, type, side, amount)
                        if order:
                            print(f"Position closed: {order} with PnL: {pnl}%")
                else:
                    if positions and df["STOCHRSIk_14_14_3_3"].iloc[-1] < 20:
                        # Place a market sell order to close the trade
                        order = bybit.create_contract_v3_order(symbol, type, 'buy', amount)
                            
                        print(f"Exit signal order placed: {order}")
                        pass
                    else:
                        pnl <= -5 or pnl >= 10
                        print(f"Closing position for {symbol} with PnL: {pnl}%")
                        side = 'buy'
                        order = bybit.create_contract_v3_order(symbol, type, side, amount)
                        if order:
                            print(f"Position closed: {order} with PnL: {pnl}%")
                


                


# Run the trading_bot function
trading_bot(df)



schedule.every(1).minutes.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(40)
