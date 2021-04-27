
import pandas as pd
import numpy as np
import time
from time import struct_time
import streamlit as st
from math import pi
from bokeh.plotting import figure
from bokeh.io import output_notebook, show
from bokeh.resources import INLINE
from bokeh.models import LinearAxis, Range1d,HBar,HoverTool
from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d
output_notebook(resources=INLINE)
from bokeh.plotting import figure, output_file, show
import tweepy
import re
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

def BTC_drop_change(OHLCV,start,end,change_low,change_high,v_start,v_end,volume,vchange_low,vchange_high): 

            filtered=OHLCV[(OHLCV['Date'] >= start) & (OHLCV['Date'] <= end)]
            print('filtered',len(filtered))
            Volume_filtered=OHLCV[(OHLCV['Date'] >= v_start) & (OHLCV['Date'] <= v_end)]
            v1=filtered.groupby(['symbol']).agg(old_volume=('Volume','mean'))
            a=Volume_filtered.groupby(['symbol']).agg(new_volume=('Volume','mean'))
            v=a.join(v1, on='symbol')
            v=v[v['old_volume']<volume]
            OHLCV_change=filtered[(filtered['change']>=change_low) & (filtered['change']<=change_high)].sort_values('change')
            OHLCV_change=OHLCV_change.join(v, on='symbol')
            OHLCV_change['volume_change']=100*(OHLCV_change['old_volume']-OHLCV_change['new_volume'])/OHLCV_change['new_volume']
            OHLCV_change=OHLCV_change[(OHLCV_change['volume_change']>=vchange_low) &(OHLCV_change['volume_change']<=vchange_high)]
           
            return OHLCV_change
        
def Volume_change(OHLCV,start1,end1,start2,end2,change1,change2):
            df11=OHLCV[(OHLCV['Date'] >= start1) & (OHLCV['Date'] <= end1)]
            df22=OHLCV[(OHLCV['Date'] >= start2) & (OHLCV['Date'] <= end2)]
            df1=df11.groupby(['symbol']).agg(old_volume=('Volume','mean'))
            df2=df22.groupby(['symbol']).agg(new_volume=('Volume','mean'))
            print(df2)
            df=df1.join(df2, on='symbol')
            print(df)
            df['volume_change']=100*(df['old_volume']-df['new_volume'])/df['new_volume']
            print(df)
            df=df11.join(df, on='symbol')
            df=df[(df['volume_change']>=change1) &(df['volume_change']<=change2)]
            return df

def group_tweets(df_tweet,symbol='BTC',freq='1h'):
              symbol='#'+symbol
              a=df_tweet[df_tweet.coin==symbol]
              a=a.groupby([pd.Grouper(key='time', freq='1h'),'destination','source']).sum()
              a.reset_index(inplace=True)
              ex_list=['#Binance','#Coinbase','#Bitstamp','#OKEx','#Huobi', '#Kucoin', 'Huobi', '#Bitfinex']
              a['coin_price']=a.amount_USD/a.coin_count
              outfrom=a[a['source'].isin(ex_list)]
              into=a[a['destination'].isin(ex_list)]
              into.set_index('time',inplace=True)
              outfrom.set_index('time',inplace=True)
              return into,outfrom
          
            
def df_adjust_step(df_bid_ex,df_ask_ex,quote,step_percentage,prices,flag,percentage_fromprice=100):      
         df_bid_adjusted=pd.DataFrame()
         df_ask_adjusted=pd.DataFrame()
         symbols=df_bid_ex.symbol.unique()
         for symbol in symbols:
                        price=prices[symbol]                    
                            #df_bid,df_ask=calculate_price(df_bid,df_ask,quote)
                        df_bid=df_bid_ex[df_bid_ex['symbol']==symbol]    
                        maxs=df_bid["bid"].max()
                        mins=df_bid["bid"].min()
                        if(maxs>price*2):
                              maxs=price*2
                        if(mins<price/2):
                              mins=price/2
                        step=mins*step_percentage/100
                        if((mins>0) and (step>0) and (maxs>0)):
                            df_bid=df_bid.groupby(pd.cut(df_bid["bid"], np.arange(mins, maxs+step, step))).agg({'amount':'sum','bid':'mean','amount_BTC':sum,'amount_USDT':sum,'price_diff':'mean','distance_from_max':'mean'})
                            df_bid['price']=df_bid.index
                        df_bid['symbol']=symbol
                        
                        df_bid_adjusted=pd.concat([df_bid,df_bid_adjusted],ignore_index=True)
                        if flag==1:
                            df_bid_adjusted=df_bid_adjusted[abs(df_bid_adjusted['price_diff'])<=percentage_fromprice]
                        elif flag==2:
                            
                            df_bid_adjusted=df_bid_adjusted
         print(df_bid_adjusted)
        
         for symbol in symbols:    
                        df_ask=df_ask_ex[df_ask_ex['symbol']==symbol]  
                        price=prices[symbol]                      
                        mins=df_ask["ask"].min()
                        maxs=df_ask["ask"].max()
                        if(maxs>price*2):
                            maxs=price*2
                        if(mins<price/2):
                            mins=price/2
                            
                        step=mins*step_percentage/100
                        if((mins>0) and (step>0) and (maxs>0)):
                            df_ask=df_ask.groupby(pd.cut(df_ask["ask"], np.arange(mins, maxs+step, step))).agg({'amount':'sum','ask':'mean','amount_BTC':sum,'amount_USDT':sum,'price_diff':'mean','distance_from_max':'mean'})
                            df_ask['price']=df_ask.index
                        df_ask['symbol']=symbol
                        df_ask_adjusted=pd.concat([df_ask,df_ask_adjusted],ignore_index=True)
                        if flag==1:
                            df_ask_adjusted=df_ask_adjusted[-1*(df_ask_adjusted['price_diff'])<=percentage_fromprice]

                        elif flag==2:
                            
                            df_ask_adjusted=df_ask_adjusted
                            
                        
         return df_bid_adjusted,df_ask_adjusted ,prices     
     
def get_bidask(df_bid_adjusted,df_ask_adjusted,BTC=0,USDT=0):
        ask_filtered=pd.DataFrame()
        bid_filtered=pd.DataFrame()
       
        if float(BTC)>0:
            ask_filtered=df_ask_adjusted[df_ask_adjusted['amount_BTC']>float(BTC)]
            bid_filtered=df_bid_adjusted[df_bid_adjusted['amount_BTC']>float(BTC)]
        elif float(USDT)>0:
            ask_filtered=df_ask_adjusted[df_ask_adjusted['amount_USDT']>float(USDT)]
            bid_filtered=df_bid_adjusted[df_bid_adjusted['amount_USDT']>float(USDT)]
        return ask_filtered,bid_filtered
    
    
def plot_bokeh(into,outfrom,df):
              #into=self.into
              #outfrom=self.outfrom
              #output_file("label.html", title="label.py example")
              z=outfrom.drop(['destination','source','amount_USD'],axis=1)
              z=z.reset_index()
              print(z)
              #source = ColumnDataSource(data=z)
              df_ = df.copy()
              symbol=df['symbol'].unique()[0]
              inc = df_.Close > df_.Open
              dec = df_.Open > df_.Close
              #up=z.coin_price>z.Close
              #down=z.coin_price<z.Close
              _tools_to_show = 'box_zoom,pan,save,hover,reset,tap,wheel_zoom'        
            
              p = figure(width=1000, height=910 ,x_axis_type="datetime", tools=_tools_to_show,title = symbol)
              w = 1*60*60*800
             # p = figure(x_axis_type="datetime", plot_width=1100, plot_height=500, title = symbol)
              p.segment(df_.index, df_.High, df_.index, df_.Low, color="black")
              p.vbar(df_.index[inc], w, df_.Open[inc], df_.Close[inc], fill_color="green", line_color="red")
              p.vbar(df_.index[dec], w, df_.Open[dec], df_.Close[dec], fill_color="red", line_color="green")
              #p.y_range = Range1d(df.Close.min(), df.Close.max()+10000)
              #p.extra_y_ranges = {"NumStations": Range1d(start=0, end=a.coin_count.max()+10000)}
              #p.add_layout(LinearAxis(y_range_name="NumStations"), 'right')
              #y_range_name='NumStations'
              average_in=into.coin_count.mean()
              average_out=outfrom.coin_count.mean()
              p.triangle(outfrom.index, outfrom.coin_price,name="mycircle",angle =3.14,fill_alpha=0.5,color='green',size=5*outfrom.coin_count/average_out)
              p.triangle(into.index, into.coin_price,name="mycircle",fill_alpha=0.5 ,color='red',size=5*into.coin_count/average_in)
              #labels = LabelSet(x='time', y='coin_price', text='coin_count', level='glyph', x_offset=5, y_offset=5, source=source, render_mode='canvas')
              tooltips=[('price', 'into.coin_price'),('amount', 'into.coin_count')]
              p.add_tools(HoverTool(tooltips=tooltips))

              #p.add_layout(labels)


              st.bokeh_chart(p)
     
def vwap(df):
    q = df.quantity.values
    p = df.price.values
    return df.assign(vwap=(p * q).cumsum() / q.cumsum())

def pump_prepare(since,tf):

        d={}
        data=pd.DataFrame()
        order=pd.DataFrame()
        #since = ex.milliseconds () - (m*86400000/24)
        since = st.text_input("start date to check",'2021-04-24 00:00:00')
        since = ex.parse8601(since)
        #since = '2021-04-13 12:00:00'
        #since=pd.Timestamp(since)
        #int(datetime.timestamp(since))
        
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
        
        final.drop(columns=['timestamp'],inplace=True)
        
def get_marketcap():
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
          'start':'1',
          'limit':'5000',
          'convert':'USD'
        }
        headers = {
          'Accepts': 'application/json',
          'X-CMC_PRO_API_KEY': '3b6d4be6-4877-4590-8491-7226da4ecc05',
        }

        session = Session()
        session.headers.update(headers)

        try:
          response = session.get(url, params=parameters)
          data = json.loads(response.text)
          df=pd.DataFrame(data['data'])
          #df.quote[0]['BTC']['market_cap']
          df['market_cap']=df.quote.apply(lambda x : x['USD']['market_cap'])
          df['Volume']=df.quote.apply(lambda x : x['USD']['volume_24h'])
          df['price']=df.quote.apply(lambda x : x['USD']['price'])
        except (ConnectionError, Timeout, TooManyRedirects) as e:
          print(e)
        return df