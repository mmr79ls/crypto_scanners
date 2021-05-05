# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 23:35:02 2021

@author: mraslan
"""

import ccxt
import pandas as pd
from crypto_func import *
from crypto2 import crypto
import streamlit as st
import numpy as np
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

#symbols=ex.symbols
def comp_prev(a,shift=1):
    return (a.High-a.Close.shift(shift))*100/a.Close.shift(shift)#a.High


@st.cache(allow_output_mutation=True)
def get_marketcap():
            df=get_marketcap()
            
            df['coin']=df['symbol']
            df.drop(columns='symbol',axis=1,inplace=True)
            cols=['coin','date_added','max_supply','circulating_supply','total_supply','market_cap','Volume24h','price']
            df=pd.DataFrame(df,columns=cols)
            df.set_index('coin',inplace=True)
            print('market')
            return df

@st.cache(allow_output_mutation=True)
def search_pump(sampling,start):
        
        raw_all=pd.DataFrame()
        price_all=pd.DataFrame()
        data_all=pd.DataFrame()

        ex=ccxt.binance()
        ex.load_markets()
        f=pd.DataFrame(ex.fetch_markets())
        symbols=f[f['active']==True].symbol.unique()
        #symbols=ex.symbols
        def comp_prev(a,shift=1):
            return (a.High-a.Close.shift(shift))*100/a.Close.shift(shift)#a.High
        
        s=[]
        u=[]
        for symbol in symbols:
            if symbol.split('/')[1]=='BTC':
                s.append(symbol)
            if symbol.split('/')[1]=='USDT':
                u.append(symbol.split('/')[0])
        
        #since=since = ex.milliseconds () - (75*86380000)
        symbols=[]
        for i in s:
                if i.split('/')[0] not in u:
                    symbols.append(i)

       
        for symbol in symbols:
      
            #print(symbol)
            raw,data,price=get_trades(ex,symbol,sampling,start)
            raw_all=pd.concat([raw,raw_all],ignore_index=True)
            price_all=pd.concat([price,price_all],ignore_index=True)
            data_all=pd.concat([data,data_all],ignore_index=True)
        raw_all.set_index('datetime',inplace=True)
        raw_all=raw_all.sort_values('datetime')
        price_all['Time']=pd.to_datetime(price_all['Time']*1000000)
        data_all.set_index('Date',inplace=True)
        new=pd.DataFrame()
        new['symbol']=raw_all['symbol']
        new['price_buy']=raw_all['price']['buy']
        new['cost_buy']=raw_all['cost']['buy']
        new['price_sell']=raw_all['price']['sell']
        new['cost_sell']=raw_all['cost']['sell']
        new['spread']=raw_all['spread']
        new['spread_change']=raw_all['spread_change']
        new['buysell_ratio']=raw_all['buysell_ratio']
        new['vol']=raw_all['vol']
        new['buysell_difference']=raw_all['buysell_difference']
        
        new['buysell_to_vol%']=raw_all['buysell_to_vol%']
        new.index=raw_all.index
        raw_all=new.drop_duplicates()
        data_all=data_all.drop_duplicates()
        new=[]
        raw_all=raw_all.reset_index()
        data_all=data_all.reset_index()
        raw_all['datetime']=pd.to_datetime(raw_all['datetime'], utc = True)
        data_all['Date']=pd.to_datetime(data_all['Date'], utc = True)
        merged=pd.merge(data_all, raw_all,  how='left', left_on=['Date','symbol'], right_on = ['datetime','symbol'])
        
        #merged=merged[merged['Date']>=pd.to_datetime(t, utc = True)[0]]
        print(merged)        
        return merged

start=st.text_input('start time','2021-05-04 08:00:00')
sampling=st.text_input('resolution 1T,5T,1h      T=mins',value='1T')
change=st.number_input('% to filter on change of price',value=3)
#df=get_marketcap()
df=pd.read_csv('market_cap.csv')
merged=search_pump(sampling,start)
print(merged)  
merged['coin']=merged.symbol.apply(lambda x : x.split('/')[0])
merged.set_index('coin',inplace=True)
final=merged.drop(columns=['Time','Open','Close','High','Low','datetime']).reset_index()
print(final)
#.join(df)

action=st.selectbox('volume filter',['yes','no'])
if action=='yes':
    
    change_buysell1=st.number_input('% buy/sell',value=0.0)
    change_buysell2=st.number_input('% buy/sell',value=100)
    
    f1=final[(final['buysell_to_vol%']<max(change_buysell1,change_buysell2)) & (final['buysell_to_vol%']>min(change_buysell1,change_buysell2))]
    st.dataframe(f1)
    f2=f1.groupby('symbol').agg({'buysell_to_vol%':'count' }).merge(final.groupby('symbol').agg({'cost_buy':'sum','cost_sell':'sum','vol':'sum','buysell_difference':'sum'}),on='symbol')
    f2['buysell_ratio%']=f2.cost_buy/f2.cost_sell
    f2['buysell_to_vol%_actual']=f2.buysell_difference/f2.vol
    #f2=f1.groupby('symbol').agg({'change':'mean','cost_buy':'sum','cost_sell':   'sum','vol':'sum' })
    #f2['change']=f2.cost_buy/f2.cost_sell
    st.dataframe(f2)
elif action=='no':
    f=final[final['change']>change]
    st.dataframe(f)
    f2=f.groupby('symbol').agg({'change':'count' }).merge(final.groupby('symbol').agg({'cost_buy':'sum','cost_sell':'sum','vol':'sum','buysell_difference':'sum'}),on='symbol')
    f2['buysell_ratio%']=f2.cost_buy/f2.cost_sell
    f2['buysell_to_vol%_actual']=f2.buysell_difference/f2.vol
    st.dataframe(f2)
    print(f2)
    