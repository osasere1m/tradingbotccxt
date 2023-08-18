

import ccxt
import pandas as pd
import pandas_ta as ta
import time
import schedule

# Step 1: Import the necessary libraries

# Step 2: Set up the exchange connection

kucoin = ccxt.kucoin({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,
    
})

# Run the trading_bot function
trading_bot(df)



schedule.every(2).minutes.do(trading_bot, df)
# Call the trading_bot function every 2 minutes
while True:
    schedule.run_pending()
    time.sleep(40)