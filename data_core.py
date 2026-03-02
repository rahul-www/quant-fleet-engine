import yfinance as yf
import pandas as pd
import sqlite3

def update_vault(ticker):
    symbol = ticker
    stock = yf.Ticker(symbol)
    interval = '1d'
    data_info = stock.history(period='6mo',interval=interval)

    data_info['SMA_20'] = data_info['Close'].rolling(window=20).mean()
    data_info['STD_20'] = data_info['Close'].rolling(window=20).std()
    
    data_info['Upper Band'] = data_info['SMA_20'] + (data_info['STD_20']*2)
    data_info['Lower Band'] = data_info['SMA_20'] - (data_info['STD_20']*2)
    data_info = data_info.dropna()

    data_info['Price_Change'] = data_info['Close'].diff()
    data_info['Gains'] = data_info['Price_Change'].clip(lower=0)
    data_info['Losses'] = data_info['Price_Change'].clip(upper=0).abs()

    data_info['Avg_Gains'] = data_info['Gains'].rolling(window=14).mean()
    data_info['Avg_Losses'] = data_info['Losses'].rolling(window=14).mean()

    data_info['RS'] = data_info['Avg_Gains'] / data_info['Avg_Losses']
    data_info['RSI'] = 100 - (100/(1+data_info['RS']))
    data_info = data_info.dropna()
    
    data_info['EMA_12'] = data_info['Close'].ewm(span=12,adjust=False).mean()
    data_info['EMA_26'] = data_info['Close'].ewm(span=26,adjust=False).mean() 
    
    data_info['MACD'] = data_info['EMA_12'] - data_info['EMA_26']
    data_info['SIGNAL'] = data_info['MACD'].ewm(span=9,adjust=False).mean()
    
    data_info['HISTOGRAM'] = data_info['MACD'] - data_info['SIGNAL']
    data_info = data_info.dropna()

    pd.set_option('display.max_columns',None)
    pd.set_option('display.width',None)
    print(f"Historical Stock Data of {symbol}")
    data_info = data_info[['Close','Price_Change','RSI','Lower Band','Upper Band','EMA_12','EMA_26','MACD','SIGNAL','HISTOGRAM']]
    conn = sqlite3.connect('quant_data.db')
    data_info.to_sql(f"{symbol}",conn, if_exists='replace',index= True)
   

    




