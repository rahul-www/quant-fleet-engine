import sqlite3
import pandas as pd
def backtest_process(capital_invest,shares,symbol):
    conn = sqlite3.connect('quant_data.db')
    df = pd.read_sql_query(f"SELECT * FROM [{symbol}]",conn)
    
    if df is None or df.empty:
        empty_df = pd.DataFrame()
        return 0, 0, 0, ["ERROR: Data Vault is empty or corrupted for this symbol."], empty_df, [], [], [], [], [], []


    start_capital=capital_invest
    capital = start_capital
    shares_owned = shares
    trade_log = []
    trade_count = 0
    buy_dates = []
    buy_price = []
    sell_dates = []
    sell_price = []
    force_date = []
    force_price = []
    total_profit = 0
    in_position = False

    for i in range(5,len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            prev_macd = prev_row['MACD']
            prev_signal = prev_row['SIGNAL']
            current_macd = row['MACD']
            current_signal = row['SIGNAL']
            bullish_crossover = (prev_macd <= prev_signal) and (current_macd > current_signal)
            bearish_crossover = (prev_macd >= prev_signal) and (current_macd < current_signal)
            date  = str(row['Date'])[:10] 
            price = row['Close']
            rsi = row['RSI']
            lower_band = row['Lower Band']
            upper_band = row['Upper Band']
            bullish_crossover = (prev_macd <= prev_signal) and (current_macd > current_signal)
            bearish_crossover = (prev_macd >= prev_signal) and (current_macd < current_signal)
            
            rsi_oversold = df['RSI'].iloc[i-5 : i+1].min() < 40
            lower_band_broken = df['Close'].iloc[i-5 : i+1].min() < lower_band
            
            rsi_overbought = df['RSI'].iloc[i-5 : i+1].max() > 60
            uppper_band_broken = df['Close'].iloc[i-5 : i+1].max() > upper_band
            
                        
        ## BUY Logic  
            if bullish_crossover and (rsi_oversold or lower_band_broken):
                if capital >= price and shares_owned == 0:
                    if not in_position:
                
                        shares_owned = int(capital/price)
                        total_price = price*shares_owned
                        capital = capital - (shares_owned*price)
                        trade_log.append(f"Bought : {date} | Price: Rs{price:.2f} | MACD: {current_macd:.2f} | SIGNAL: {current_signal:.2f} | RSI: {rsi:.2f} | Shares: {shares_owned} | Lower Band: {lower_band:.2f} | Total Price: Rs {total_price:,.2f} | Remaining Capital: Rs {capital:,.2f} ")
                        trade_count += 1
                        buy_dates.append(date)
                        buy_price.append(price)
                        in_position = True
                    
                
            elif bearish_crossover and (rsi_overbought or uppper_band_broken):
                if shares_owned > 0:
                    if in_position:
                        sell_cash = shares_owned * price
                        capital = capital + sell_cash
                        trade_log.append(f"Sold : {date} | Price: Rs{price:.2f} | MACD: {current_macd:.2f} | SIGNAL: {current_signal:.2f} | RSI: {rsi:.2f} | Upper Band: {upper_band:.2f} | Selling Price: Rs {sell_cash:,.2f} | Wallet Balance: Rs {capital:,.2f} | Cashed Out ")      
                        shares_owned = 0
                        trade_count += 1
                        total_profit = capital - start_capital
                        sell_dates.append(date)
                        sell_price.append(price)
                        in_position = False
                
    if shares_owned > 0:
            final_date = df.iloc[-1]['Date'][:10]
            final_rsi = df.iloc[-1]['RSI']
            upper_band = df.iloc[-1]['Upper Band']
            final_price = df.iloc[-1]['Close']
            final_cash = shares_owned*final_price      
            capital = capital + (shares_owned * final_price)
            total_profit = capital - start_capital
            trade_count += 1
            force_date.append(final_date)
            force_price.append(final_price)
            trade_log.append("Conditions Not Met for Proper Sell. Running a Force Sell Simulation")
            trade_log.append(f"Force Sell: {final_date} | Price: Rs {final_price:.2f} | RSI: {final_rsi:.2f} | Shares Sold: {shares_owned} | Cash Generated: Rs {final_cash:.2f} | End Capital: Rs {capital:.2f}")
    return(capital,total_profit,trade_count,trade_log,df,buy_dates,buy_price,sell_dates,sell_price,force_date,force_price)
            

            