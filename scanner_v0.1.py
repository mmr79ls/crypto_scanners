#!/usr/bin/env python
# coding: utf-8
import ccxt
from crypto1 import crypto
import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
from crypto_func import BTC_drop_change,group_tweets,df_adjust_step,get_bidask
import time

def draw_filtered(ask_filtered,bid_filtered,symbol):
    sns.set(rc={'figure.figsize':(200,150)})
    A=ask_filtered[ask_filtered['symbol']==symbol].copy()
    b=bid_filtered[bid_filtered['symbol']==symbol].copy()
    if (len(A)==0) & (len(b)==0):
        ('symbol '+ symbol +' NOT found')
        
    else:
        #A=A[A['exchange'].isin(exchange)]
        A['flag']='ask'
        A['price_avg']=A['ask']
        #b=b[b['exchange'].isin(exchange)]
        b['flag']='bid'
        b['price_avg']=b['bid']
        if len(A)>15:
            bidask=pd.concat([A[:15],b[-15:-1]])
        else:
            bidask=pd.concat([A,b])
        bidask=bidask.sort_values('price_avg',ascending=False)

        g=sns.catplot(x="amount_BTC",y="price", kind="bar",hue='flag', data=bidask).set(title='BID/ASK for : '+symbol,label='big')
        print('graph in progress')
        for ax in g.axes.flat:
            for label in ax.get_yticklabels():
                label.set_rotation(0)
            for label in ax.get_xticklabels():
                label.set_rotation(90)
        g.fig.set_size_inches(10,5)
        return g



quote=st.selectbox('Symbol',['USDT','BTC'])
#symbol=st.text_input('enter the symbol')

@st.cache(allow_output_mutation=True)
def scan(quote):
    print(quote)
    a=crypto('binance',quote)  
    df_bid_ex,df_ask_ex,prices  =a.scanner()
    print('scan done')
    st.write('last updated on '+str(time.time()))
    #symbols=a.bid.symbol.unique()
    #time_tuple=(2021, 3, 30, 00, 00, 00, 0, 00, 0)
    #OHLCV=a.get_OHLCV(time_tuple,'1h')
    #a.get_tweets()
    return a,df_bid_ex,df_ask_ex,prices 
@st.cache(allow_output_mutation=True)
def percentage_stept(df_bid_ex,df_ask_ex,quote,step_percentage,prices,percentage_fromprice ):
    print(quote)
    df_bid_adjusted,df_ask_adjusted=df_adjust_step(df_bid_ex,df_ask_ex,quote,step_percentage,prices,percentage_fromprice)
    
    return df_bid_adjusted,df_ask_adjusted 


a,df_bid_ex,df_ask_ex,prices=scan(quote)

flag=st.button('rescan again')
if flag==1:
    a,df_bid_ex,df_ask_ex,prices=scan(quote)  
    
st.balloons()
percentage=st.number_input('Enter percantage for orderbook aggregation',0.1)
percentage_fromprice=st.number_input('enter the distance from current price',0.1)
df_bid_adjusted,df_ask_adjusted=percentage_stept(df_bid_ex,df_ask_ex,quote,percentage,prices,percentage_fromprice)
filter=st.text_input('input the minmum aggregated value filter in 4 BTC or 4 USDT','4 BTC')


f=list(filter.split())
if f[1]=='BTC':
    BTC_filter=float(f[0])
    ask_filtered,bid_filtered=get_bidask(df_bid_adjusted,df_ask_adjusted,BTC=BTC_filter,USDT=0)
elif f[1]=='USDT':
    USDT_filter=float(f[0])
    ask_filtered,bid_filtered= get_bidask(df_bid_adjusted,df_ask_adjusted,BTC=0,USDT=USDT_filter)

temp=pd.concat([ask_filtered,bid_filtered])
symbols=temp.symbol.unique()
st.write('Number of symbols detected are ' + str(len(symbols)))
symbol=st.selectbox('Symbol',symbols)
show=st.button('Show graph')
if show:
    fig=draw_filtered(ask_filtered,bid_filtered,symbol)
    st.pyplot(fig)
#start=st.date_input('select the start Date')
#end=st.date_input('select the End Date')
#start_time=st.time_input('select start time')
#end_time=st.time_input('select end time')

#exchange=ccxt.binance()
#df=pd.DataFrame(exchange.fetchTrades(symbol,limit=100000))
#st.dataframe(df)
#exchange.fetchOHLCV (symbol, timeframe = '1m', since = start,