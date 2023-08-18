import ccxt

import pandas as pd
from datetime import datetime

import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})

#parameter
symbol = 'LTC/USDT'
timeframe = '1d'
since = exchange.parse8601('2020-01-01T00:00:00Z')
limit = 200


ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

#df = pd.read_csv("Ltc_data1d.csv")
df.tail()

#Check if NA values are in data
df.isna().sum()

#Engulfing pattern signals
import random
def Revsignal1(df1):
    length = len(df1)
    high = list(df1['high'])
    low = list(df1['low'])
    close = list(df1['close'])
    open = list(df1['open'])
    signal = [0] * length
    bodydiff = [0] * length

    for row in range(1, length):
        bodydiff[row] = abs(open[row]-close[row])
        bodydiffmin = 0.003
        if (bodydiff[row]>bodydiffmin and bodydiff[row-1]>bodydiffmin and
            open[row-1]<close[row-1] and
            open[row]>close[row] and 
            #open[row]>=close[row-1] and close[row]<open[row-1]):
            (open[row]-close[row-1])>=+0e-5 and close[row]<open[row-1]):
            signal[row] = 1
        elif (bodydiff[row]>bodydiffmin and bodydiff[row-1]>bodydiffmin and
            open[row-1]>close[row-1] and
            open[row]<close[row] and 
            #open[row]<=close[row-1] and close[row]>open[row-1]):
            (open[row]-close[row-1])<=-0e-5 and close[row]>open[row-1]):
            signal[row] = 2
        else:
            signal[row] = 0
        #signal[row]=random.choice([0, 1, 2])
        #signal[row]=1
    return signal
df['signal1'] = Revsignal1(df)
df[df['signal1']==1].count()

print(df)
#Target
def mytarget(df1, barsfront):
    length = len(df1)
    high = list(df1['high'])
    low = list(df1['low'])
    close = list(df1['close'])
    open = list(df1['open'])
    trendcat = [None] * length
    
    piplim = 300e-5
    for line in range (0, length-1-barsfront):
        for i in range(1,barsfront+1):
            if ((high[line+i]-max(close[line],open[line]))>piplim) and ((min(close[line],open[line])-low[line+i])>piplim):
                trendcat[line] = 3 # no trend
            elif (min(close[line],open[line])-low[line+i])>piplim:
                trendcat[line] = 1 #-1 downtrend(short)
                break
            elif (high[line+i]-max(close[line],open[line]))>piplim:
                trendcat[line] = 2 # uptrend(long)
                break
            else:
                trendcat[line] = 0 # no clear trend  
    return trendcat

df['Trend'] = mytarget(df,3)
#df.head(30)

print(df)

import numpy as np
conditions = [(df['Trend'] == 1) & (df['signal1'] == 1),(df['Trend'] == 2) & (df['signal1'] == 2)]
values = [1, 2]
df['result'] = np.select(conditions, values)

trendId=1
print(df[df['result']==trendId].result.count()/df[df['signal1']==trendId].signal1.count())
df[ (df['Trend']!=trendId) & (df['signal1']==trendId) ] # false positives

#library for plotting
dfpl = df[400:450]
import plotly.graph_objects as go
from datetime import datetime

fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close'])])

fig.show()