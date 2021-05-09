#!/usr/bin/env python
# coding: utf-8
import ccxt
from crypto2 import crypto
import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
from crypto_func import BTC_drop_change,group_tweets,df_adjust_step,get_bidask
import time
import datetime
from streamlit import caching


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
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
     

    #dt = datetime.fromordinal(time.time()).strip('YYYY/MM/DD hh:mm')
    #st.write('last updated on '+str(time.time()))
    #symbols=a.bid.symbol.unique()
    #time_tuple=(2021, 3, 30, 00, 00, 00, 0, 00, 0)
    #OHLCV=a.get_OHLCV(time_tuple,'1h')
    #a.get_tweets()
    return a,df_bid_ex,df_ask_ex,prices 
@st.cache(allow_output_mutation=True)
def percentage_stept(df_bid_ex,df_ask_ex,quote,step_percentage,prices,flag,percentage_fromprice ):
    print(quote)
    df_bid_adjusted,df_ask_adjusted,prices=df_adjust_step(df_bid_ex,df_ask_ex,quote,step_percentage,prices,flag,percentage_fromprice)
    
    return df_bid_adjusted,df_ask_adjusted ,prices


a,df_bid_ex,df_ask_ex,prices=scan(quote)

flag=st.button('rescan again')
if flag==1:
    caching.clear_cache()
    a,df_bid_ex,df_ask_ex,prices=scan(quote)  
    

percentage=st.number_input('Enter percantage for orderbook aggregation',value=1.1)
action=st.selectbox('Select the function you want   distance from price/  max price within distance',['distance from price','Max price in distance','Price distance between bid and ask'])
if action=='distance from price':
    percentage_fromprice=st.number_input('enter the distance from current price',value=1000)
    st.write('You are now checking the Orders within %')
    df_bid_adjusted,df_ask_adjusted,prices=percentage_stept(df_bid_ex,df_ask_ex,quote,percentage,prices,1,percentage_fromprice)
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
   # ask_filtered.set_index('symbol',inplace=True)
   # bid_filtered.set_index('symbol',inplace=True)
   # temp=ask_filtered.join(bid_filtered,lsuffix='_ask', rsuffix='_bid')
    #temp=temp.drop(['index','symbol_ask'],axis=1)
    #st.dataframe(temp.set_index('symbol_bid'))
    st.dataframe(ask_filtered.set_index('symbol'))
    st.dataframe(bid_filtered.set_index('symbol'))
    #t.dataframe(ask_filtered.set_index('symbol'))
    st.write('Number of symbols detected are ' + str(len(symbols)))
    symbol=st.selectbox('Symbol',symbols)
    show=st.button('Show graph')
    if show:
        fig=draw_filtered(ask_filtered,bid_filtered,symbol)
        st.pyplot(fig)    
        
elif action=='Max price in distance':
    percentage_fromprice=st.number_input('enter the % to search for max order',value=3)
    st.write('You are now checking the max order within %')
    df_bid_adjusted,df_ask_adjusted,prices=percentage_stept(df_bid_ex,df_ask_ex,quote,percentage,prices,2,percentage_fromprice)
    temp_bid=pd.DataFrame()
    temp_ask=pd.DataFrame()
    df_bid_adjusted=df_bid_adjusted.reset_index()
    l=df_bid_adjusted.groupby('symbol').amount_BTC.idxmax()
    df_bid_adjusted=df_bid_adjusted[df_bid_adjusted.index.isin(l)]
    l=df_ask_adjusted.groupby('symbol').amount_BTC.idxmax()
    df_ask_adjusted=df_ask_adjusted[df_ask_adjusted.index.isin(l)]
    ask_filtered=df_ask_adjusted[abs(df_ask_adjusted.price_diff)<percentage_fromprice]
    bid_filtered=df_bid_adjusted[abs(df_bid_adjusted.price_diff)<percentage_fromprice]
    st.write('Number of symbols in ask detected are ' + str(len(ask_filtered)))
    st.write('Number of symbols in bid detected are ' + str(len(bid_filtered)))
    temp=pd.concat([ask_filtered,bid_filtered])
    symbols=temp.symbol.unique()
    ask_filtered.set_index('symbol',inplace=True)
    bid_filtered.set_index('symbol',inplace=True)
    temp=ask_filtered.join(bid_filtered,lsuffix='_ask', rsuffix='_bid')
    #temp=temp.drop(['index','symbol_ask'],axis=1)
    st.dataframe(temp)
    #st.dataframe(bid_filtered.set_index('symbol'))
    #t.dataframe(ask_filtered.set_index('symbol'))
    st.write('Number of symbols detected are ' + str(len(symbols)))
    symbol=st.selectbox('Symbol',symbols)
    show=st.button('Show graph')
    if show:
        fig=draw_filtered(ask_filtered.reset_index(),bid_filtered.reset_index(),symbol)
        st.pyplot(fig)
elif action=='Price distance between bid and ask':
    #percentage_fromprice=st.number_input('enter the % to search for max order',value=3)
    percentage_fromprice=1000000
    st.write('Price distance between bid and ask')
    df_bid_adjusted,df_ask_adjusted,prices=percentage_stept(df_bid_ex,df_ask_ex,quote,percentage,prices,2,percentage_fromprice)
    temp_bid=pd.DataFrame()
    temp_ask=pd.DataFrame()
    df_bid_adjusted=df_bid_adjusted.reset_index()
    l=df_bid_adjusted.groupby('symbol').amount_BTC.idxmax()
    df_bid_adjusted=df_bid_adjusted[df_bid_adjusted.index.isin(l)]
    l=df_ask_adjusted.groupby('symbol').amount_BTC.idxmax()
    df_ask_adjusted=df_ask_adjusted[df_ask_adjusted.index.isin(l)]
    
    
    ask_filtered=df_ask_adjusted[abs(df_ask_adjusted.price_diff)<percentage_fromprice]
    bid_filtered=df_bid_adjusted[abs(df_bid_adjusted.price_diff)<percentage_fromprice]
    st.write('Number of symbols in ask detected are ' + str(len(ask_filtered)))
    st.write('Number of symbols in bid detected are ' + str(len(bid_filtered)))
    temp=pd.concat([ask_filtered,bid_filtered])
    symbols=temp.symbol.unique()
    ask_filtered.set_index('symbol',inplace=True)
    bid_filtered.set_index('symbol',inplace=True)
    temp=ask_filtered.join(bid_filtered,on='symbol',lsuffix='_ask', rsuffix='_bid')
    temp['distance']=abs(temp['price_diff_ask'])+abs(temp['price_diff_bid'])
    filter1=st.number_input('filter for distance between highest bid and highest ask 1')
    filter2=st.number_input('filter for distance between highest bid and highest ask 2')
    temp=temp[(temp['distance']>min(filter1,filter2) )& (temp['distance']<max(filter1,filter2) )]
    #temp=temp.drop(['index','symbol_ask'],axis=1)
    st.dataframe(temp)
    #st.dataframe(bid_filtered.set_index('symbol'))
    #t.dataframe(ask_filtered.set_index('symbol'))
    st.write('Number of symbols detected are ' + str(len(symbols)))
    symbol=st.selectbox('Symbol',symbols)
    show=st.button('Show graph')
    if show:
        fig=draw_filtered(ask_filtered.reset_index(),bid_filtered.reset_index(),symbol)
        st.pyplot(fig)
    


    #print(df_ask_adjusted)
    
    #print(prices)
    #PRICE FORMULA PRICES LOOKUP




#start=st.date_input('select the start Date')
#end=st.date_input('select the End Date')
#start_time=st.time_input('select start time')
#end_time=st.time_input('select end time')

#exchange=ccxt.binance()
#df=pd.DataFrame(exchange.fetchTrades(symbol,limit=100000))
#st.dataframe(df)
#exchange.fetchOHLCV (symbol, timeframe = '1m', since = start,