#idea of three ema 
#when the long ema crossover above the short and middle take long
#when the long ema crossover below the short and middle take short


Write me biance trading python script for perpetual future using ccxt, pandas and time library and pair DOGE/USDT, leverage of 10 , position size of 10, create limit order using a simple triple EMA cross over strategy for long and short. First load the market 


creating order
order = exchange.futuresPrivatePostOrderCreate(symbol, {
            
            'side' : 'buy',
            'order_type' : 'Limit',
            'qty' : 10,
            'time_in_force': "GoodTillCancel",
            'price' : ask_price
})



#bybit future contract enable
 exchange.options["dafaultType"] = 'future'
 exhange.load_markets()

 #create order
 createOrder(symbol, types, side, amount, params)

 fetchOrder(orderId, symbol)
 fetchPositions(symbol)
