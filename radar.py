
import sqlite3
import pandas as pd
import requests
import time

def send_message(msg):
    
    token = "8745402111:AAFhy3up5nsPl5xvgARc9Y2INGGCH39tw6w"
    chat_id = 7812981881
    api_link = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}" 
    response = requests.get(api_link) 


def telegram_radar(symbol_list):
    
    for symbol in symbol_list:
        try:

            conn = sqlite3.connect('quant_data.db')
                
            df = pd.read_sql_query(f"SELECT * FROM [{symbol}]",conn)
            date  = str(df.iloc[-1]['Date'])[:10]
            final_price = df.iloc[-1]['Close']
            rsi = df.iloc[-1]['RSI']
            lower_band = df.iloc[-1]['Lower Band']
            upper_band = df.iloc[-1]['Upper Band']
            prev_macd = df.iloc[-2]['MACD']
            prev_signal = df.iloc[-2]['SIGNAL']
            current_macd = df.iloc[-1]['MACD']
            current_signal = df.iloc[-1]['SIGNAL']
            
            bullish_crossover = (prev_macd <= prev_signal) and (current_macd > current_signal)
            bearish_crossover = (prev_macd >= prev_signal) and (current_macd < current_signal)
                
            if rsi < 30 and final_price < lower_band and bullish_crossover:
                message = f"Hey. There is a significant shift toward a price Decrease on this stock:\n Stock: {symbol} \nDate: {date}  \nPrice: Rs{final_price:.2f} \n MACD: {current_macd} \n SIGNAL: {current_signal} \nRSI: {rsi:.2f} \nLower Band: {lower_band} \n BUY at your OWN RISK!"
                send_message(message)
                
            elif rsi >70 and final_price > upper_band and bearish_crossover:
                message = f"Hey. There is a significant shift toward a price Increase on this stock: \n Stock: {symbol} \nDate: {date} \nPrice: Rs{final_price:.2f} \n MACD: {current_macd} \n SIGNAL: {current_signal} \nRSI: {rsi:.2f} \nUpper Band: {upper_band} \n SELL at your OWN RISK! "
                send_message(message)
                
            else:
                message = f"{symbol}\nThe Stock is calm Hold ur Position\n Date: {date} \nPrice: Rs{final_price:.2f} \n MACD: {current_macd} \n SIGNAL: {current_signal} \n RSI: {rsi:2f}"
                send_message(message)
                
            time.sleep(2)
            
        except Exception as e:
            print(f"Error Scanning{symbol}: {e}")
            continue        
 

      