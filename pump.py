# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 18:15:24 2021

@author: mraslan
"""

import ccxt
import pandas as pd
import streamlit as st
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
ex=ccxt.binance()
ex.load_markets()

symbols=ex.symbols
def comp_prev(a,shift=1):
    return (a.High-a.Low)*100/a.High
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
filters=st.number_input('Enter the filter')
tf=st.text_input('Enter the time frame  1m,5m,...')
#m=st.number_input('enter the number of days back')
d={}
data=pd.DataFrame()
order=pd.DataFrame()
since = ex.milliseconds () - (2*86400000)

raw=pd.DataFrame()
#symbols=['VIA/BTC','SKY/BTC','CDT/BTC']
for symbol in symbols:
    a=pd.DataFrame(ex.fetch_trades(symbol,limit=10000))
    price=pd.DataFrame(ex.fetch_ohlcv(symbol,tf,since=since,limit=10000),columns=['Time','Open','High','Low','Close','Volume'])
    price['symbol']=symbol
    price['change']=comp_prev(price,1)
    a['symbol']=symbol
    raw=pd.concat([a,raw])
    data=pd.concat([price,data])
    z=a.groupby('side').amount.sum()[0]/a.groupby('side').amount.sum()[1]
    y=a[a['side']=='buy'].sort_values('amount',ascending=False).cost.sum()
    x=a[a['side']=='sell'].sort_values('amount',ascending=False).cost.sum()
    yy=a[a['side']=='buy'].sort_values('amount',ascending=False).cost.max()
    xx=a[a['side']=='sell'].sort_values('amount',ascending=False).cost.max()
    d[symbol]=[z,y,x,yy,xx]
    a=pd.DataFrame(d)
    a=a.T
    a.columns=['ratio','buy total','sell total','buy max','sell max']
    z=pd.DataFrame(d,columns=['ratio','buy total','sell total','buy max','sell max'])
    order=pd.concat([a,order])
data['Date']=pd.to_datetime(data['Time']*1000000)
test=data
order['symbol']=order.index
order=order.reset_index()
order.drop(columns=['index'],axis=1,inplace=True)
order=order.drop_duplicates()
suspects=test[test['change']>=filters].groupby('symbol').Open.count().sort_values(ascending=False)
final=pd.DataFrame()
for suspect in suspects.index:
    a=order[order['symbol']==suspect]
    a['count']=suspects[suspect]
    final=pd.concat([a,final])

st.dataframe(final.sort_values(['count','ratio','sell total'],ascending=False))
print(final.symbol.unique())
symbol=st.selectbox('Symbol',final.symbol.unique())
st.dataframe(raw[raw['symbol']==symbol])

