import streamlit as st
import pandas as pd
import sqlite3
from data_core import update_vault
from backtester import backtest_process
from radar import telegram_radar
import plotly.graph_objects as go
import threading
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx

st.set_page_config(page_title="Quant engine", layout = "wide")

st.sidebar.title("Command Centre")
st.sidebar.write("Welcome")

page = st.sidebar.radio("Select a Mode:",
                        ["Data","Simulation"])

target_symbol = st.text_input("Enter multiple symbols seperated by commas","INFY.NS").split(',')
## Data Vault
if page == "Data":
    st.title("Data Of the Stocks")
    if st.button("Fetch data"):
       with st.spinner("Fetching Data....."):
           for symbol in target_symbol:
            data_base = update_vault(symbol)
            conn = sqlite3.connect('quant_data.db')
            df = pd.read_sql_query(f"SELECT * FROM [{symbol}]",conn)
            conn.close()
            st.subheader(f"{symbol}")
            st.dataframe(df.tail(50))      
## BackTest Analysis
elif page == "Simulation":
    st.title("Simulated Trading Ground")
    st.subheader("Run a Simulation Trade based on the Historical Data of the Market")
    capital_options = st.radio(
                        
                        "Select Invsetment mode:",
                        options = ['PER MARKET','TOTAL CAPITAL'],
                        index = 0,
                        key="investment_mode_v2"
                        )
    st.write(f"The machine currently sees:{capital_options}")
  
    assume_capital = st.number_input("Enter Hypothetical Starting Capital (ex: 10000)",key="sim_capital")
    share = st.number_input("Enter Hypothetical Starting Shares (ex: 10)",key="sim_share")
    if st.button("Start Simulation"):
        with st.spinner("Analyzing for User Data....."):
                st.title("Portfolio Scoreboard")
                st.columns(3)
                col1,col2,col3 = st.columns(3)
                with col1:
                    st.subheader("Portfolio Investment")
                    investment_placeholder = col1.empty()
                with col2:
                    st.subheader("Portfolio Profit")
                    profit_placeholder = col2.empty()
                with col3:
                    st.subheader("Portfolio Trades")
                    trade_placeholder = col3.empty()        
                total_portfolio_profit = 0
                total_portfolio_trades = 0
                total_capital_investment = 0

                for symbol in target_symbol:
                    symbol = symbol.strip()
                    n = len(target_symbol)
                    if capital_options == 'PER MARKET':
                        simulation_capital = assume_capital
                    elif capital_options == 'TOTAL CAPITAL':
                        simulation_capital = assume_capital / n    
                   
                    st.subheader(f"{symbol}")
                    final_cap,total_profit,trades,logs,catch_df,catch_b_dates,catch_b_price,catch_s_dates,catch_s_price,catch_f_dates,catch_f_price = backtest_process(simulation_capital,share,symbol)
                    total_portfolio_profit += total_profit
                    total_portfolio_trades += trades
                    total_capital_investment += simulation_capital 
                    with st.expander(f"Simulation Results:{symbol}"):       
                        if trades == 0:
                            st.warning(f"**SIMULATION FAILED: ZERO TRADES EXECUTED.**\n\nThe market for {target_symbol} never experienced a significant dip during this timeline. The RSI never dropped below 30, and the price never crossed the Lower Band. The bot remained disciplined and protected your capital.")
                        else:
                            fig = go.Figure()
                            col1,col2,col3 = st.columns(3)
                            with col1:
                                st.subheader("Simulated Balance")
                                st.metric(label="Balance: ",value = f"Rs {final_cap:,.2f}")
                            with col2:
                                        st.subheader("Hypothetical Profit/Loss")
                                        st.metric(label="Profit: ",value= f"Rs {total_profit:,.2f}")
                            with col3:
                                        st.subheader("Total Simulated Trades")
                                        st.metric(label="Trades: ",value=trades)
                            with st.expander("Show Historical Trade Analysis"):   
                                        for row in logs:
                                            st.write(row) 
                                            
                            st.dataframe(catch_df)
                            fig.add_trace(go.Scatter(
                                        
                                        x = catch_df['Date'],
                                        y = catch_df['Close'],
                                        name = 'Stock Price',
                                        line = dict(color = 'white'),
                                        hovertemplate="Date: %{x}<br>Price: Rs %{y:,.2f}<extra></extra>"
                                    ))
                                                
                            fig.add_trace(go.Scatter(
                                        
                                        x = catch_df['Date'],
                                        y = catch_df['Upper Band'],
                                        name = 'Upper Band',
                                        line = dict(color = 'red'),
                                        hovertemplate="Date: %{x}<br>Price: Rs %{y:,.2f}<extra></extra>"
                                    ))
                                    
                            fig.add_trace(go.Scatter(
                                        
                                        x = catch_df['Date'],
                                        y = catch_df['Lower Band'],
                                        name = 'Lower Band',
                                        line = dict(color = 'green'),
                                        hovertemplate="Date: %{x}<br>Price: Rs %{y:,.2f}<extra></extra>"
                                    ))
                                    
                            fig.add_trace(go.Scatter(
                                        
                                    x = catch_b_dates,
                                    y = catch_b_price,
                                    mode = 'markers',
                                    name = 'Buy Signal',
                                    marker = dict(symbol = 'triangle-up',color = 'green',size = 14),
                                    hovertemplate = "BUY Trigger<br>Date: %{x}<br>Price: Rs %{y:,.2f}<extra></extra>"   
                                    )) 
                                    
                            fig.add_trace(go.Scatter(
                                        
                                        x = catch_s_dates,
                                        y = catch_s_price,
                                        mode = 'markers',
                                        name = 'Sell Signal',
                                        marker = dict(symbol = 'triangle-down', color = 'red', size = 14),
                                        hovertemplate = "SELL Trigger<br>Date: %{x}<br>Price: Rs %{y:,.2f}<extra></extra>"
                                    ))
                                    
                            fig.add_trace(go.Scatter(
                                        
                                        x = catch_f_dates,
                                        y = catch_f_price,
                                        mode = 'markers',
                                        name = 'Force Sell Signal',
                                        marker = dict(symbol = 'triangle-down', color = 'yellow', size = 14),
                                        hovertemplate = " FORCE SELL Trigger<br>Date: %{x}<br>Price: Rs %{y:,.2f}<extra></extra>"
                                    ))
                                    
                            st.plotly_chart(fig, use_container_width = True)
                
                investment_placeholder.metric(label="Investment: ",value= f"Rs {total_capital_investment:,.2f}")
                profit_placeholder.metric(label="Portfolio Profit: ",value= f"Rs {total_portfolio_profit:,.2f}")
                trade_placeholder.metric(label="Portfolio Trades: ",value= f"Rs {total_portfolio_trades}")           
               
  
                            

    









