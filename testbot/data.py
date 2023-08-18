import ccxt
import pandas as pd
from datetime import datetime, timedelta

def download_historical_data(symbol, timeframe, since):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.to_csv('LTC_USDT_daily.csv')



symbol = 'ETH/USDT'
timeframe = '1d'#15m
since = int((datetime.now() - timedelta(days=1000)).timestamp() * 1000)  # 24 hours ago
download_historical_data(symbol, timeframe, since)

"""""
import ccxt
import pandas as pd

symbol = 'LTC/USDT' # trading symbol
timeframe = '1d' # timeframe (1d = 1 day)
start_date = '2022-01-01' # start date (YYYY-MM-DD)
end_date = '2023-04-27' # end date (YYYY-MM-DD)

# create an instance of the Binance exchange
exchange = ccxt.binance()

# load historical data using the fetch_ohlcv method
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=exchange.parse8601(start_date), 
                             limit=1000, params={'endTime': exchange.parse8601(end_date)})

# convert the data into a pandas DataFrame object and set the timestamp column as the index
header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
df = pd.DataFrame(ohlcv, columns=header).set_index('Timestamp')
df.index = pd.to_datetime(df.index, unit='ms')

# optionally save the DataFrame object as a CSV file
df.to_csv('LTC_USDT_daily.csv')
"""