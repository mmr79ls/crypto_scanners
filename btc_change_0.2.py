# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 17:05:54 2021

@author: mraslan
"""

from unicorn_binance_rest_api.unicorn_binance_rest_api_manager import BinanceRestApiManager
     
import ccxt
from crypto_okex import crypto
import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
from crypto_func import BTC_drop_change,group_tweets,plot_bokeh,Volume_change
from datetime import datetime
from finta import TA
import matplotlib.pyplot as plt
from streamlit import caching
import streamlit_analytics

import plotly.express as px
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
@st.cache(allow_output_mutation=True)
def OHLCV(percentage,quote,time_tuple=(2021, 3, 20, 00, 00, 00, 0, 00, 0),tf='1h',exchange='binance'):
        a=crypto(exchange,quote)  
        
        #df_tweet=a.get_tweets()
        #time_tuple=(2021, 3, 30, 00, 00, 00, 0, 00, 0)
        #into,outfrom=group_tweets(df_tweet,coin,tf)
        into=outfrom=0
        OHLCV=a.get_OHLCV(time_tuple,tf)
        return OHLCV,into,outfrom
@st.cache(allow_output_mutation=True)
def scan_RSI(ex,symbol,tf,RSI=40,flag=0,starttime='2021-09-02 00:00:00',end='2021-09-03 00:00:00',trend=1):
    start_date=ex.parse8601(starttime) 
    df=pd.DataFrame(ex.fetch_ohlcv(symbol,tf,since=start_date))
    df.columns=['Time','open','high','low','close','volume']
    df['price_delta']=(df.close-df.open)*100/df.close
    
    df['Date']=pd.to_datetime(df['Time']*1000000)
    df=df[df['Date']<end]
    x=TA.RSI(df,9)
    df['RSI']=x
    df['RSI_delta']=(df.RSI-df.RSI.shift(1))*100/df.RSI
    count=0
    indx=np.array([])
    rng=np.array([])
    indx1=[]
    #rng1=[]
    len1=[]
    i=0
    if trend==0:
            for i in range(len(x)):
                if x[i]>RSI and x[i-1]<RSI:
                    if len(rng)>2:
                       # rng1.append(rng)
                        len1.append(len(rng))
                        indx1.append(indx)
                    indx=np.array([])
                    rng=np.array([])
                if x[i]>RSI:
                    continue
                if x[i]<RSI:
                    indx=np.append(indx,i)
                    rng=np.append(rng,x[i])
                    i+=1
    elif trend==1:
            for i in range(len(x)):
                if x[i]<RSI and x[i-1]>RSI:
                    if len(rng)>2:
                       # rng1.append(rng)
                        len1.append(len(rng))
                        indx1.append(indx)
                    indx=np.array([])
                    rng=np.array([])
                if x[i]<RSI:
                    continue
                if x[i]>RSI:
                    indx=np.append(indx,i)
                    rng=np.append(rng,x[i])
                    i+=1
       
    rs=pd.DataFrame([indx1,len1]).T
    rs.columns=['ind','count']
    if len(rs)>0:
            if flag==1:
                #largest trend

                rs.sort_values('count',ascending=False)[:1].ind.to_list()[0][0]
                i=rs.sort_values('count',ascending=False)[:1].index[0]
                l=len(rs.sort_values('count',ascending=False)[:1].ind[i])
                filter=rs.sort_values('count',ascending=False)[:1].ind.to_list()[0][0]
                l=df[df.index>filter][:l-1]
            elif flag==0:
                #newest trend
                i=rs.ind[len(rs)-1][0]
                l=len(rs.ind[len(rs)-1])
                l=df[df.index>i][:l-1]
    else:
        l=[]
    return l
def price_calculator():
        exchange=st.selectbox('Exchange',['binance','okex','gateio'])
        if exchange=='binance':
            ex=ccxt.binance()
        elif exchange=='okex':    
            ex=ccxt.okex()
        elif exchange=='gateio':
            ex=ccxt.gateio()
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
program=st.selectbox('btc change or profit calculator',['BTC_change','Price_calculator','RSI','candle_search'])
if program=='Price_calculator':
    change,profit,profit_BTC=price_calculator()


if program=='BTC_change':
   
        with streamlit_analytics.track():    
            quote=st.selectbox('Symbol',['USDT','BTC'])
            exchange=st.selectbox('Exchange',['binance','okex','gateio'])
            #percentage=st.number_input('Enter percantage for orderbook aggregation',0.5)
            flag=st.button('rescan again')
            if flag==1:
                caching.clear_cache()
                percentage=1


                time_tuple=(2021, 3, 20, 00, 00, 00, 0, 00, 0)
                OHLCV1,into,outfrom=OHLCV(percentage,quote,time_tuple,'1h',exchange) 

            percentage=1


            time_tuple=(2021, 3, 20, 00, 00, 00, 0, 00, 0)
            coin=st.text_input('Enter the coin you want to check from whale bot','BTC')
            print(coin)
            tf=st.text_input('Time frame (1m/1h/4h/1d/1w)','1h')
            OHLCV1,into,outfrom=OHLCV(percentage,quote,time_tuple,'1h',exchange)
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
                    symbols=OHLCV1['symbol'].unique()
                    #a=['USDC/USDT' , 'EUR/USDT', 'TUSD/USDT' , 'BUSD/USDT' , 'PAX/USDT' , 'AUD/USDT' , 'SUSD/USDT' , 'GBP/USDT' , 'PAXG/USDT']

                    for symbol in symbols:# OHLCV1['symbol']:
                        # if symbol not in a:
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
                    symbols=closes['symbol'].drop_duplicates().to_list()
                    closes.set_index('symbol',inplace=True)
                    if exchange=='binance':
                       ex=ccxt.binance()
                    elif exchange=='okex':    
                       ex=ccxt.okex()
                    elif exchange=='gateio':
                       ex=ccxt.gateio()

                    symbol=st.sidebar.radio('Symbol',symbols)

                     #tf=st.selectbox('Time Frame',['1m','5m','15m','1h','4h','1d','1w','1M'])
                     #percent_price=st.number_input('Enter the % from price to calculate',1.0)
                   #num_close=st.number_input('Enter the number of Closes to filter',0)

                    df=pd.DataFrame(ex.fetch_ohlcv(symbol,tf,limit=1000),columns=['Time','Open','High','Low','Close','Volume'])
                    df['Date']=pd.to_datetime(df['Time']*1000000)

                    #strt=df['Date'].min()
                    #st.write('Data loaded from date '+str(strt))
                    #start_filter = st.text_input("The start of duration to check",'2021-08-11 23:00:00')
                    #start_filter=pd.Timestamp(start_filter)
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
                    st.dataframe(closes[closes.index==symbol])
                    #p=plot_bokeh(into,outfrom,df)

            #st.bokeh_chart(p)
            #show(p)
@st.cache(allow_output_mutation=True)                
def rsi(ex,tf,RSI,flag,starttime,end,trend):
    df_rsi=pd.DataFrame()
    for symbol in symbols:
                l=scan_RSI(ex,symbol,tf,RSI,flag,starttime,end,trend)
                
                if len(l)<=1:
                        continue
                l['symbol']=symbol
                df_rsi=pd.concat([df_rsi,l])
    return df_rsi
if  program=='RSI':
     with streamlit_analytics.track():  
           exchange=st.selectbox('Exchange',['binance','okex','gateio'])
           if exchange=='binance':
               ex=ccxt.binance()
           elif exchange=='okex':    
               ex=ccxt.okex()
           elif exchange=='gateio':
               ex=ccxt.gateio()
           
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
           #symbol=st.sidebar.radio('Symbol',symbols)
           tf=st.selectbox('Time Frame',['1m','5m','15m','1h','4h','1d','1w','1M'])
           
           #percent_price=st.number_input('Enter the % from price to calculate',1.0)
           #num_close=st.number_input('Enter the number of Closes to filter',0)
           tf='4h'
           
           RSI=st.number_input('Enter the RSI filter ',10)
           flag=st.selectbox('for longest series select 1, for newest series select 0',[0,1])
           
           starttime=st.text_input('Enter the start of period to search for','2021-09-01 00:00:00')
           end=st.text_input('Enter the end of period to search for','2021-09-02 00:00:00')
           trend=st.selectbox('for up trend select 1  (>70) , for downtrend select 0  (<40)',[0,1])
           df_rsi=rsi(ex,tf,RSI,flag,starttime,end,trend)
           flag2=st.button('rescan again')
           if flag2==1:
               caching.clear_cache()
               df_rsi=rsi(ex,tf,RSI,flag,starttime,end,trend)
           ssymbols=df_rsi.groupby('symbol').RSI.count().sort_values(ascending =False).reset_index()
           
           symbol=st.sidebar.radio('Symbol',ssymbols.symbol)
           st.dataframe(ssymbols)
           st.dataframe(df_rsi[df_rsi['symbol']==symbol])
def comp_prev(a,shift=1):
        return (a.Close-a.Close.shift(shift))*100/a.Close          
if  program=='candle_search':
      with streamlit_analytics.track():                 
           exchange=st.selectbox('Exchange',['binance','okex','gateio'])
           if exchange=='binance':
               ex=ccxt.binance()
           elif exchange=='okex':    
               ex=ccxt.okex()
           elif exchange=='gateio':
               ex=ccxt.gateio()
           
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
           #symbol=st.sidebar.radio('Symbol',symbols)
           tf=st.selectbox('Time Frame',['1m','5m','15m','1h','4h','1d','1w','1M'])
           starttime=st.text_input('Enter the start of period to search for','2021-09-01 00:00:00')
           
           end=st.text_input('Enter the end of period to search for','2021-09-02 00:00:00')
           candle=st.number_input('enter the candle change %',0.0)
           delta_filter=st.number_input('enter the Delta to filter %',0.0)
           end=pd.Timestamp(end)
           start=st.text_input('the history you need  x days ago','2 days')
           ubra = BinanceRestApiManager()
           #def get_ohlcv_candle(ex,symbols,starttime,end,candle,tf):
           def get_ohlcv_candle(ubra,symbols,interval,start,delta_filter,starttime,end,candle):
                start_str=start+' ago UTC'
                OHLCV1=pd.DataFrame()
                for symbol in symbols:
                          symbol=symbol.replace("/","")
                          df=pd.DataFrame(ubra.get_historical_klines(symbol=symbol,interval=interval,start_str=start_str),columns=['Time','Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades','Taker buy base asset volume','Taker buy quote asset volume','ignore'])
                          df=df.astype( dtype={
                               'Open': float,
                               'High': float,
                               'Low': float,
                               'Close': float,
                               'Volume': float,

                               'Quote asset volume': float,
                               'Number of trades': float,
                                'Taker buy base asset volume': float,
                               'Taker buy quote asset volume': float,
                               'ignore': float

                                           })
                          #df=df[df['Time']==df['Time'].max()]
                          df['symbol']=symbol
                          df['interval']=interval
                          df['change']=100*(df['High']-(df['Low']))/(df['Low'])
                          df['Date']=pd.to_datetime(df['Time']*1000000)
                          df['interval']=df['interval']
                          df['Buy']=(df['Quote asset volume'])-(df['Taker buy quote asset volume'])
                          df['Delta']=((df['Quote asset volume'])-(df['Taker buy quote asset volume']))-(df['Taker buy quote asset volume'])
                          df=df[abs(df['change'])>=candle]
                          df=df[abs(df['Delta'])>=delta_filter]
                          df['percentage']=df['Delta']*100/df['Quote asset volume']
                          OHLCV1=pd.concat([df,OHLCV1],ignore_index=True)
                OHLCV1=OHLCV1.set_index('Date')
                OHLCV1=OHLCV1[(OHLCV1.index>=starttime) & (OHLCV1.index<=end)]

                return OHLCV1
               
           #df=get_ohlcv_candle(ex,symbols,starttime,end,candle,tf)
           df=get_ohlcv_candle(ubra,symbols,tf,start,delta_filter,starttime,end,candle)
           flag2=st.button('rescan again')
           if flag2==1:
               caching.clear_cache()
               #df=get_ohlcv_candle(ex,symbols,starttime,end,candle,tf)
               df=get_ohlcv_candle(ubra,symbols,tf,start,delta_filter,starttime,end,candle)
          
           st.dataframe(df)
