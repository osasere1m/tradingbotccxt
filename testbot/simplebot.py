import ccxt
import numpy as np
import talib as ta

from scipy.optimize import curve_fit

# Create an instance of the Bybit exchange object
exchange = ccxt.bybit({
    'apiKey': '',
    'secret': '',
    'test': True,  # required by Bybit
})

exchange.set_sandbox_mode(True) # activates testnet mode




# Define the Lorentzian function
def lorentzian(x, a, x0, gamma):
    return a * gamma**2 / ((x - x0)**2 + gamma**2)



# Set the symbol and timeframes
symbol = 'LTC/USDT'
timeframe_ohlcv = '1d'
timeframe_rsi = '1w'



# Load historical price data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe_ohlcv)
prices = np.array([candle[4] for candle in ohlcv])

# Load historical RSI data
rsi = ta.RSI(prices, timeperiod=14)
rsi_weekly = rsi[::7]

# Fit the Lorentzian curve to the data
x = np.arange(len(prices))
popt, pcov = curve_fit(lorentzian, x, prices)

# Calculate the slope of the curve at the last data point
last_slope = lorentzian(len(prices), *popt) - lorentzian(len(prices)-1, *popt)

# Get the current balance and open orders
balance = exchange.fetch_balance()
open_orders = exchange.fetch_open_orders(symbol)

# Set the leverage to 5
leverage = 5

# Calculate the amount to trade based on available balance
amount = balance['USDT']['free'] * 0.1 / prices[-1]

# Calculate the entry price based on the last trade
if len(open_orders) > 0:
    if open_orders[0]['side'] == 'buy':
        entry_price = float(open_orders[0]['info']['avg_entry_price'])
    else:
        entry_price = float(open_orders[0]['info']['avg_entry_price'])
else:
    entry_price = 0

# Check if there is an open position and calculate the PNL
if len(open_orders) > 0:
    position = exchange.fetch_position(symbol)
    if position['side'] == 'buy':
        pnl = (prices[-1] - float(position['avgEntryPrice'])) / float(position['avgEntryPrice'])
    else:
        pnl = (float(position['avgEntryPrice']) - prices[-1]) / float(position['avgEntryPrice'])
else:
    pnl = 0

# Check if the stop-loss should be moved to the entry price
if abs(pnl) >= 0.5:
    if len(open_orders) > 0:
        if open_orders[0]['side'] == 'buy':
            stop_loss_price = entry_price
            exchange.create_order(symbol, type='stop_loss_limit', side='buy', amount=balance['LTC']['free'], price=stop_loss_price, params={'leverage': leverage})
        else:
            stop_loss_price = entry_price
            exchange.create_order(symbol, type='stop_loss_limit', side='sell', amount=balance['LTC']['free'], price=stop_loss_price, params={'leverage': leverage})

# Classify the trend as bullish or bearish based on Lorentzian curve and execute trades if RSI confirms the trend


if last_slope > 0 and rsi_weekly[-1] > 50:
# If the trend is bullish and there are no open orders, execute a buy order
    if len(open_orders) == 0:
        buy_price = prices[-1] * 1.01
        stop_loss_price = buy_price * 0.95
        exchange.create_order(symbol, type='limit', side='buy', amount=amount, price=buy_price, params={'leverage': leverage})
        exchange.create_order(symbol, type='stop_loss_limit', side='sell', amount=amount, price=stop_loss_price, params={'leverage': leverage})
    # If the trend is bullish and there is an open sell order, cancel it and execute a buy order
    elif open_orders[0]['side'] == 'sell':
        exchange.cancel_order(open_orders[0]['id'], symbol)
        buy_price = prices[-1] * 1.01
        stop_loss_price = buy_price * 0.95
        exchange.create_order(symbol, type='limit', side='buy', amount=amount, price=buy_price, params={'leverage': leverage})
        exchange.create_order(symbol, type='stop_loss_limit', side='sell', amount=amount, price=stop_loss_price, params={'leverage': leverage})
elif last_slope < 0 and rsi_weekly[-1] < 50:
    # If the trend is bearish and there are no open orders, execute a sell order
    if len(open_orders) == 0:
        sell_price = prices[-1] * 0.99
        stop_loss_price = sell_price * 1.05
        exchange.create_order(symbol, type='limit', side='sell', amount=amount, price=sell_price, params={'leverage': leverage})
        exchange.create_order(symbol, type='stop_loss_limit', side='buy', amount=amount, price=stop_loss_price, params={'leverage': leverage})
# If the trend is bearish and there is an open buy order, cancel it and execute a sell order
elif open_orders[0]['side'] == 'buy':
    exchange.cancel_order(open_orders[0]['id'], symbol)
    sell_price = prices[-1] * 0.99
    stop_loss_price = sell_price * 1.05
    exchange.create_order(symbol, type='limit', side='sell', amount=amount, price=sell_price, params={'leverage': leverage})
    exchange.create_order(symbol, type='stop_loss_limit', side='buy', amount=amount, price=stop_loss_price, params={'leverage': leverage})


