import backtesting
import pandas as pd
import numpy as np

class SMARSI_Strategy(backtesting.Strategy):
    n = 22
    def init(self):
        close = self.data.Close
        self.sma = self.I(backtesting.lib.SMA, close, self.n)
        self.rsi = self.I(backtesting.indicators.RSI, close, self.n)
    
    def next(self):
        if self.data.Close[-1] > self.sma[-1] and self.data.Close[-2] <= self.sma[-2] and self.rsi[-1] > 70:
            self.buy()
        elif self.data.Close[-1] < self.sma[-1] and self.data.Close[-2] >= self.sma[-2] and self.rsi[-1] < 30:
            self.sell()

def main():
    df = pd.read_csv('LTC_USDT_daily.csv', parse_dates=True, usecols = [0,1,2,3,4], names  = ["Timestamp","Open","High", "Low", "Close"])
    print(df)
    bt = backtesting.Backtest(df, SMARSI_Strategy, cash=10000, commission=.002, exclusive_orders=True)
    output = bt.run()
    bt.plot()

if __name__ == '__main__':
    main()
