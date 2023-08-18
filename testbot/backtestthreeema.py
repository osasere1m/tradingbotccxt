import pandas as pd

# Load historical data
data = pd.read_csv('/Users/godfrey/Documents/devtools/tradingbot/bybit/historical_data.csv')

# Define initial parameters
balance = 10000
position_size = 10
leverage = 10
fees = 0.001

# Define function to simulate trades
def backtest(data):
    balance_history = [balance]
    position_history = [0]

    for i in range(len(data)):
        # Apply EMA calculations
        ema1 = data['close'].ewm(span=10).mean()
        ema2 = data['close'].ewm(span=20).mean()
        ema3 = data['close'].ewm(span=50).mean()

        # Generate signal
        if ema3[i] < ema1[i] and ema3[i] < ema2[i]:
            # Generate buy signal
            if position_history[-1] == 0:
                position_history.append(position_size)
                balance_history.append(balance - position_size * data['close'][i])
            else:
                position_history.append(position_history[-1])
                balance_history.append(balance_history[-1])
        elif ema3[i] > ema1[i] and ema3[i] > ema2[i]:
            # Generate sell signal
            if position_history[-1] > 0:
                position_history.append(0)
                balance_history.append(balance_history[-1] + position_size * data['close'][i])
            else:
                position_history.append(position_history[-1])
                balance_history.append(balance_history[-1])
        else:
            # Hold position
            position_history.append(position_history[-1])
            balance_history.append(balance_history[-1])

    return balance_history, position_history

# Run backtest
balance_history, position_history = backtest(data)

# Calculate performance metrics
profit_loss = balance_history[-1] - balance
max_drawdown = (max(balance_history) - min(balance_history)) / max(balance_history)

print(backtest)