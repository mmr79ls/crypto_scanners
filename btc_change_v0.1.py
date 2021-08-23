# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 18:32:12 2021

@author: mraslan
"""

import ccxt
from crypto2 import crypto
import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
from crypto_func import BTC_drop_change,group_tweets,plot_bokeh,Volume_change
from datetime import datetime

import matplotlib.pyplot as plt
from streamlit import caching
import plotly.express as px
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
@st.cache(allow_output_mutation=True)
def OHLCV(percentage,quote,time_tuple=(2021, 3, 20, 00, 00, 00, 0, 00, 0),tf='1h'):
        a=crypto('binance',quote)  
        
        #df_tweet=a.get_tweets()
        #time_tuple=(2021, 3, 30, 00, 00, 00, 0, 00, 0)
        #into,outfrom=group_tweets(df_tweet,coin,tf)
        into=outfrom=0
        OHLCV=a.get_OHLCV(time_tuple,tf)
        return OHLCV,into,outfrom

def price_calculator():

        ex=ccxt.binance()
        df_BTC=pd.DataFrame(ex.fetch_ohlcv('BTC/USDT','1h',limit=1),columns=['Time','Open','High','Low','Close','Volume'])
        btc_price=df_BTC.Close.values[0]
        f=pd.DataFrame(ex.fetch_markets())
        symbols=f[f['active']==True].symbol.unique()
        symbol=st.selectbox('choose the symbol',symbols)
        price=st.number_input('enter the price',value=0.005)
        amount=st.number_input('enter the amount' ,value=0.001)
        df=pd.DataFrame(ex.fetch_ohlcv(symbol,'1h',limit=1),columns=['Time','Open','High','Low','Close','Volume'])
        change=(df.Close.values[0]-price)*100/price
        if symbol.split('/')[1]=='USDT':
            profit=(df.Close.values[0]-price)*amount
            profit_BTC=profit/btc_price
            st.write('current price= '+ str(df.Close.values[0] ))
            st.write('Profit percentage= '+ str(change))
            st.write('profits are '+ str(profit) +' USDT')
            st.write('profits are '+ str(profit_BTC) + ' BTC')
        elif symbol.split('/')[1]=='BTC':
            profit=(df.Close.values[0]-price)*amount
            profit_BTC=profit*btc_price
            st.write('current price= '+ str(df.Close.values[0] ))
            st.write('Profit percentage= '+ str(change))
            st.write('profits are '+ str(profit) + 'BTC')
            st.write('profits are '+ str(profit_BTC) + 'USDT')
        print('% of Change ',change)
        print('profit is ',profit)
        print('profit in BTC ',profit_BTC)
        return change,profit,profit_BTC
program=st.selectbox('btc change or profit calculator',['BTC_change','Price_calculator','Close_analysis'])
if program=='Price_calculator':
    change,profit,profit_BTC=price_calculator()


if program=='BTC_change':

    quote=st.selectbox('Symbol',['USDT','BTC'])
    #percentage=st.number_input('Enter percantage for orderbook aggregation',0.5)
    flag=st.button('rescan again')
    if flag==1:
        caching.clear_cache()
        percentage=1

    
        time_tuple=(2021, 3, 20, 00, 00, 00, 0, 00, 0)
        OHLCV1,into,outfrom=OHLCV(percentage,quote,time_tuple,'1h') 
        
    percentage=1

    
    time_tuple=(2021, 3, 20, 00, 00, 00, 0, 00, 0)
    coin=st.text_input('Enter the coin you want to check from whale bot','BTC')
    print(coin)
    tf=st.text_input('Time frame (1m/1h/4h/1d/1w)','1h')
    OHLCV1,into,outfrom=OHLCV(percentage,quote,time_tuple,'1h')
    st.write('BTC price change')
    choice=st.selectbox('',['Change % check','volume filter','Close_analysis'])
    if choice=='Change % check':
            jj=str(OHLCV1[OHLCV1['symbol']=='BTC/USDT'].Date.min())
            start = st.text_input("start date to check",jj)
            start=pd.Timestamp(start)
            jj1=str(OHLCV1[OHLCV1['symbol']=='BTC/USDT'].Date.max())
            end = st.text_input("End date to check",jj1)
            end=pd.Timestamp(end)
            
            change1=st.number_input('enter the % of change in lower percentage to search for ',value=-100)
            change2=st.number_input('enter the % of change in higher percentage to search for ',value=100)
            change_low=min(change1,change2)
            change_high=max(change1,change2)
            v_start=v_end=v_volume_filter=vchange_low=vchange_high=flag=0
            OHLCV_change=BTC_drop_change(OHLCV1,start,end,change_low,change_high,v_start,v_end,v_volume_filter,vchange_low,vchange_high,flag)
            st.dataframe(OHLCV_change.set_index('Date'))
    elif choice=='volume filter':
            start = st.text_input("start date to check",'2021-04-13 12:00:00')
            start=pd.Timestamp(start)
            
            end = st.text_input("End date to check",'2021-04-13 14:00:00')
            end=pd.Timestamp(end)
            
            change1=st.number_input('enter the % of change in lower percentage to search for ',value=-100)
            change2=st.number_input('enter the % of change in higher percentage to search for ',value=100)
            change_low=min(change1,change2)
            change_high=max(change1,change2)
            v_start=st.text_input("start date for volume to sum",'2021-04-13 12:00:00')
            v_start=pd.Timestamp(v_start)
            v_end=st.text_input("end date for volume to sum",'2021-04-13 16:00:00')
            v_end=pd.Timestamp(v_end)
            #v_volume_filter=st.number_input('enter the Volume filter ( less than this volume')
            vchange1=st.number_input('enter the % of change in lower percentage in volume to search for ',value=-100)
            vchange2=st.number_input('enter the % of change in higher percentage in volume to search for ',value=100)
            vchange_low=min(vchange1,vchange2)
            vchange_high=max(vchange1,vchange2)
            v_volume_filter=0
            OHLCV_change=BTC_drop_change(OHLCV1,start,end,change_low,change_high,v_start,v_end,v_volume_filter,vchange_low,vchange_high,1)
            st.dataframe(OHLCV_change.set_index('Date'))
        
            symbol=st.text_input('input the symbol to be checked','BTC/USDT')
            f=OHLCV1[OHLCV1['symbol']==symbol]
    elif choice=='Close_analysis':
            percent_price=st.number_input('Enter the % from price to calculate',1.0)
            num_close=st.number_input('Enter the number of Closes to filter',0)
            start = st.text_input("The start of duration to check",'2021-08-11 20:00:00')
            start=pd.Timestamp(start)
                      
            closes=pd.DataFrame()
            symbols=['BTC/USDT','ICP/USDT','ETH/USDT','LTC/USDT','XRP/USDT']
            for symbol in symbols:# OHLCV1['symbol']:
                df=OHLCV1[OHLCV1['symbol']==symbol]
                #st.dataframe(df)
                df=df[df['Date']>=start]  
                step=percent_price*df.Close.max()/100
                bins=np.arange(df.Close.min(), df.Close.max() + step, step)
                hist_values,x = np.histogram(df['Close'], bins= bins,range=(df.Close.min(), df.Close.max()))
                f=pd.DataFrame(hist_values,x[1:],columns=['count'])
       
                f=f[f['count']>num_close]
                if(len(f)):
                        price=df[df['Date']==df['Date'].max()].Close.max()
                        f['change']=f.apply(lambda x :100*( x.index-price)/x.index)
                        f['Close_range_start']=f.index
                        f['Close_range_end']=f.index+step                        
                        f['price']=price
                        f['symbol']=symbol
                        f=f.reset_index()
                        #f=f.drop('index', axis=1, inplace=True)
                       
                        

                        closes=pd.concat([f,closes],ignore_index=True)
            closes=closes.sort_values('count',ascending=False)
            symbols=closes['symbol'].unqiue()
            closes.set_index('symbol',inplace=True)
            
            st.dataframe(closes)
                
                
            ex=ccxt.binance()
            
          
            symbol=st.sidebar.radio('Symbol',symbols)
      
             #tf=st.selectbox('Time Frame',['1m','5m','15m','1h','4h','1d','1w','1M'])
             #percent_price=st.number_input('Enter the % from price to calculate',1.0)
           #num_close=st.number_input('Enter the number of Closes to filter',0)

            df=pd.DataFrame(ex.fetch_ohlcv(symbol,tf,limit=10000),columns=['Time','Open','High','Low','Close','Volume'])
            df['Date']=pd.to_datetime(df['Time']*1000000)

            strt=df['Date'].min()
            st.write('Data loaded from '+str(strt))
            start = st.text_input("The start of duration to check",'2021-08-11 20:00:00')
            start=pd.Timestamp(start)
            df=df[df['Date']>start]

            price=df[df['Date']==df['Date'].max()].Close.max()
           #df=pd.DataFrame(client.get_historical_klines(symbol.replace("/",""),tf, duration),columns=['Time','Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades','Taker buy base asset volume','Taker buy quote asset volume','ignore'])
           #df=df.astype( dtype={

           #f=pd.DataFrame(ex.fetch_markets())

            print('scan')
           #df=OHLCV1[OHLCV1['symbol']==symbol]
            step=df.Close.max()*percent_price/100
           #fig=plot_hist(df,step)
            bins=np.arange(df.Close.min(), df.Close.max() + step, step)
            fig = px.histogram(df, x="Close",nbins=len(bins))
            fig.add_vline(x=price, line_width=3, line_dash="dash", line_color="red")

           #fig.show()
            st.write(fig)    
    #p=plot_bokeh(into,outfrom,df)
    
    #st.bokeh_chart(p)
    #show(p)
if  program=='Close_analysis':
                     
           ex=ccxt.binance()
           
           f=pd.DataFrame(ex.fetch_markets())
           symbs=f[f['active']==True].symbol.unique()

           s=[]
           u=[]
           for symbol in symbs:
          
              if symbol.split('/')[1]=='USDT':
                u.append(symbol)
           symbols=[]        
           for i in u:
                 t=i.find('DOWN/' or 'UP/' or 'BULL/' or 'BEAR/')
                 if(t==-1):
                        symbols.append(i)
        
           #symbol=st.selectbox('Symbol',symbols)
           symbol=st.sidebar.radio('Symbol',symbols)
           tf=st.selectbox('Time Frame',['1m','5m','15m','1h','4h','1d','1w','1M'])
           percent_price=st.number_input('Enter the % from price to calculate',1.0)
           #num_close=st.number_input('Enter the number of Closes to filter',0)
          
           df=pd.DataFrame(ex.fetch_ohlcv(symbol,tf,limit=10000),columns=['Time','Open','High','Low','Close','Volume'])
           df['Date']=pd.to_datetime(df['Time']*1000000)
           
           strt=df['Date'].min()
           st.write('Data loaded from '+str(strt))
           start = st.text_input("The start of duration to check",'2021-08-11 20:00:00')
           start=pd.Timestamp(start)
           df=df[df['Date']>start]
           
           price=df[df['Date']==df['Date'].max()].Close.max()
           #df=pd.DataFrame(client.get_historical_klines(symbol.replace("/",""),tf, duration),columns=['Time','Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades','Taker buy base asset volume','Taker buy quote asset volume','ignore'])
           #df=df.astype( dtype={
               
           #f=pd.DataFrame(ex.fetch_markets())

           print('scan')
           #df=OHLCV1[OHLCV1['symbol']==symbol]
           step=df.Close.max()*percent_price/100
           #fig=plot_hist(df,step)
           bins=np.arange(df.Close.min(), df.Close.max() + step, step)
           #hist_values= np.histogram(df['Close'], bins= bins,range=(df.Close.min(), df.Close.max()))
           #st.bar_chart(bins[1:],hist_values)
         

           fig = px.histogram(df, x="Close",nbins=len(bins))
           fig.add_vline(x=price, line_width=3, line_dash="dash", line_color="red")

           #fig.show()
           st.write(fig)
