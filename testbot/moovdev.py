import time
import schedule
import ccxt
import json
import pandas as pd
import numpy as np
from datetime import datetime, date, timezone, tzinfo

# Create an instance of the Bybit exchange object
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
})

exchange.set_sandbox_mode(True) # activates testnet mode

index_pos = 1

#time time betwn trades
pause_time = 60

#for volume calc  vol_repeat * vol_time == time ofvolume collection

vol_repeat = 11
vol_time = 5
pos_size = 20
params = {'timeInForce': 'PostOnly',}
target = 12
max_loss = -10

vol_decimal = .4


#for df 
timeframe = '4h'
limit = 100
sma = 20

#get bid and ask
