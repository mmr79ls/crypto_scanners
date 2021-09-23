# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 17:07:14 2021

@author: mraslan
"""

import ccxt
import pandas as pd
import numpy as np
from time import sleep
import time
import seaborn as sns
import streamlit as st
import time
from time import struct_time

from math import pi
#from bokeh.plotting import figure
#from bokeh.io import output_notebook, show
#rom bokeh.resources import INLINE
#from bokeh.models import LinearAxis, Range1d,HBar,HoverTool
#from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d
#output_notebook(resources=INLINE)
#from bokeh.plotting import figure, output_file, show
import tweepy
import re


class crypto():
    def __init__(self, exchange=['okex'],quote='USDT'):
      self.exchanges = ['okex']
      #self.step_percentage = step_percentage
      self.quote=quote
      Bitfinex = ccxt.okex()
      markets = Bitfinex.load_markets ()
      self.btc_usdt=pd.DataFrame(Bitfinex.fetch_ticker('BTC/USDT')).close[0]
      self.flag=0
            
    def scanner(self):
      start = time.time()
      df_ask_ex=pd.DataFrame()
      df_bid_ex=pd.DataFrame()
      #,'bitfinex','bitpanda','bybit','kraken','poloniex','kucoin','huobipro','bittrex','coinbase','bithumb']
        #bot.send_message(cid,btc_usdt
      print('BTC price is :',self.btc_usdt)

      for exchange in self.exchanges:
        
        
        id=exchange
        ex=eval ('ccxt.%s ()' % id)
        quote=self.quote
        #symbols=pairs_check(ex,quote=self.quote)  
        prices={}   
        df_pairs = pd.DataFrame(getattr(ex, 'fetchMarkets')())
        df=df_pairs[df_pairs.quote==quote]
        slist=df.symbol
        symbols=[]
        for i in slist:

            t=i.find('DOWN/' or 'UP/'or 'BULL/' or 'BEAR/' or 'USDC/' or 'EUR/' or 'TUSD/' or 'BUSD/' or 'PAX/' or 'AUD/' or 'SUSD/' or 'GBP/' or 'PAXG/') 
            if(t==-1):
                symbols.append(i)
        #symbols=pd.DataFrame(symb)
        if len(symbols)>0:
          #symbol=symbols[symbols.index==symbols.index[-1]].values[0]
          symbol=symbols[-1]
          #flag=valid_check(ex,symbol)
          #if self.flag==flag==1:
          if ex.has['fetchTicker']==True:
            self.flag=1
          else:
            self.flag=0
          if self.flag==1:
            
            length=len(symbols)
            print('Number of symbols are :',length)
            counter=0
            #symbols=['BTC/USDT','XRP/USDT','LTC/USDT']
            for symbol in symbols:
            #self.flag=valid_check(ex,symbol)
                time.sleep (ex.rateLimit / 1000) 
                
                try:
                    #ex.fetch_ticker(symbol)
                    orderbook = getattr(ex, 'fetchL2OrderBook')(symbol,1000) 
                    self.sflag=1              
                except:
                  orderbook = getattr(ex, 'fetchL2OrderBook')(symbol) 
                  self.sflag=1      
                  #self.sflag=0
                if(self.sflag==1):
                    print(symbol)
                    counter+=1
                    print(counter*100/length)
                    #orderbook = getattr(ex, 'fetchL2OrderBook')(symbol,10000)
                    a=pd.DataFrame(ex.fetch_ticker(symbol))
                    prices[symbol]=a[a.symbol==symbol].close[0]
                    price=a[a.symbol==symbol].close[0]
                    df_ask=pd.DataFrame(orderbook['asks'],columns=['ask','amount'])  
                    df_bid=pd.DataFrame(orderbook['bids'],columns=['bid','amount'])
                   #df_ask['exchange']=id
                    #df_ask['symbol']=symbol
                    #df_bid['exchange']=id
                    #df_bid['symbol']=symbol
                    #df_ask['price'] = a[a.symbol==symbol].close[0]
                    #df_bid['price'] = a[a.symbol==symbol].close[0]
                    
                    added=[id,symbol,a[a.symbol==symbol].close[0]]
                    df_ask['exchange'],df_ask['symbol'],df_ask['price']=added
                    df_bid['exchange'],df_bid['symbol'],df_bid['price']=added
                    if(self.quote=='USDT'):
                            df_bid['amount_USDT']=df_bid['amount']*df_bid['bid']
                            df_ask['amount_USDT']=df_ask['amount']*df_ask['ask']
                            df_bid['amount_BTC']=df_bid['amount_USDT']/self.btc_usdt
                            df_ask['amount_BTC']=df_ask['amount_USDT']/self.btc_usdt
                    elif(self.quote=='BTC'):
                            df_bid['amount_BTC']=df_bid['amount']*df_bid['bid']
                            df_ask['amount_BTC']=df_ask['amount']*df_ask['ask']
                            df_bid['amount_USDT']=df_bid['amount_BTC']/self.btc_usdt
                            df_ask['amount_USDT']=df_ask['amount_BTC']/self.btc_usdt
                    df_ask['price_diff']=df_ask.ask.apply(lambda x: (price-x)*100/price)
                    df_bid['price_diff']=df_bid.bid.apply(lambda x: (price-x)*100/price)
                    #if(len(df_bid)==0):
                       #  df_bid['distance_from_max']=1000
                       #  df_ask['distance_from_max']=1000
                    #else:
                       # bid_max_price=df_bid['amount_BTC'].idxmax()
                        #print(bid_max_price)
                        #ask_max_price=df_ask['amount_BTC'].idxmax()
                        #df_bid['distance_from_max']=(price-df_bid.bid[bid_max_price])*100/price
                        #df_ask['distance_from_max']=(price-df_ask.ask[ask_max_price])*100/price
                        #print(df_ask)
                        #df_ask['distance_from_max']=df_ask.ask.apply(lambda x: (price-x)*100/price)
                        #df_bid['distance_from_max']=df_bid.bid.apply(lambda x: (price-x)*100/price)
                    df_ask_ex=pd.concat([df_ask,df_ask_ex],ignore_index=True)
                    df_bid_ex=pd.concat([df_bid,df_bid_ex],ignore_index=True)  
            end = time.time()  
            elapsed = end - start
            print(elapsed)
            return df_bid_ex,df_ask_ex,prices
         
    
      
     # 
     # self.bid= df_bid_ex
     # self.ask=df_ask_ex
    def get_bidask(self,BTC=0,USDT=0):
        if float(BTC)>0:
            self.ask_filtered=self.ask[self.ask['amount_BTC']>float(BTC)]
            self.bid_filtered=self.bid[self.bid['amount_BTC']>float(BTC)]
        elif float(USDT)>0:
            self.ask_filtered=self.ask[self.ask['amount_USDT']>float(USDT)]
            self.bid_filtered=self.bid[self.bid['amount_USDT']>float(USDT)]
        return self.ask_filtered,self.bid_filtered

    def draw_bidask(self,symbol='BTC/USDT',exchange=['okex']):
          sns.set(rc={'figure.figsize':(200,150)})
          self.symbol=symbol
          a=self.ask[self.ask['symbol']==self.symbol].copy()
          b=self.bid[self.bid['symbol']==self.symbol].copy()
          if (len(a)==0) & (len(b)==0):
            print('symbol '+self.symbol+' NOT found')
          else:
            a=a[a['exchange'].isin(exchange)]
            a['flag']='ask'
            a['price_avg']=a['ask']
            b=b[b['exchange'].isin(exchange)]
            b['flag']='bid'
            b['price_avg']=b['bid']
            if len(a)>15:
                bidask=pd.concat([a[:15],b[-15:-1]])
            else:
                bidask=pd.concat([a,b])
            bidask=bidask.sort_values('price_avg',ascending=False)

            g=sns.catplot(x="amount_BTC",y="price", kind="bar",hue='flag', data=bidask).set(title='BID/ASK for : '+symbol,label='big')

            for ax in g.axes.flat:
                for label in ax.get_yticklabels():
                    label.set_rotation(0)
                for label in ax.get_xticklabels():
                    label.set_rotation(90)
            g.fig.set_size_inches(10,5)
            return g

#(2021, 3, 10, 00, 00, 00, 0, 00, 0)
#,symbol='BTC/USDT'
    def get_OHLCV(self,time_tuple,tf='1h'):
        self.time_tuple = time_tuple
        self.time_obj = struct_time(self.time_tuple)
        self.timeframe=tf
        #self.symbols=symbol

        starttime=time.mktime(self.time_obj)*1000
        my_bar = st.progress(0)
        exchange=ccxt.okex()
        exchange.load_markets()
        OHLCV=pd.DataFrame()
        print(OHLCV)
        print(exchange  )
        if exchange.has['fetchOHLCV']:
            start = time.time()
            exchanges=exchange.markets
            df_pairs = pd.DataFrame(getattr(exchange, 'fetchMarkets')())
            df=df_pairs[df_pairs.quote==self.quote]
            symbols= df.symbol
            slist=df.symbol
            symbols=[]
            for i in slist:
                t=i.find('DOWN/' or 'UP/' or 'BULL/' or 'BEAR/')
                if(t==-1):
                    symbols.append(i)
            lenght=len(symbols)
            count=0
            #symbols=['BTC/USDT']
            for symbol in symbols:
                # time.sleep wants seconds
                since = exchange.milliseconds () - (40*86400000)
                a=pd.DataFrame(exchange.fetch_ohlcv (symbol, self.timeframe,limit =10000,since=since),columns=['Time','Open','High','Low','Close','Volume'])
                a['Date']=pd.to_datetime(a['Time']*1000000)
                a['symbol']=symbol
                a['change']=self.comp_prev(a)
                OHLCV=pd.concat([a,OHLCV],ignore_index=True)
                since = exchange.milliseconds () - (80*86400000)
                count+=1
                print(count,'/',lenght)
                my_bar.progress(count/lenght)
                time.sleep (exchange.rateLimit / 2000)
                a=pd.DataFrame(exchange.fetch_ohlcv (symbol, self.timeframe,limit =10000,since=since),columns=['Time','Open','High','Low','Close','Volume'])
                a['Date']=pd.to_datetime(a['Time']*1000000)
                a['symbol']=symbol
                a['change']=self.comp_prev(a)
                OHLCV=pd.concat([a,OHLCV],ignore_index=True)
                OHLCV=OHLCV.drop_duplicates()
                time.sleep (exchange.rateLimit / 2000)
                
            end=time.time()
            print(exchange,'-',end-start)
            
            #OHLCV['Time']=OHLCV['Time'].to_datetime(OHLCV.index*1000000)
            OHLCV=OHLCV.set_index('Time')
            
            self.OHLCV=OHLCV
        
            return OHLCV
                  
    def BTC_drop_change(self,start,end,change_low,change_high):
            OHLCV=self.OHLCV      
            filtered=OHLCV[(OHLCV['Date'] >= start) & (OHLCV['Date'] <= end)]
            self.OHLCV_change=filtered[(filtered['change']>=change_low) & (filtered['change']<=change_high)].sort_values('change')
            return self.OHLCV_change
                                                       
                  
                  
                  
                  
    def comp_prev(self,a,shift=1):
        return (a.Close-a.Close.shift(shift))*100/a.Close
    
    def pairs_check(self,ex,quote='USDT'):
    
        df_pairs = pd.DataFrame(getattr(ex, 'fetchMarkets')())
        df=df_pairs[df_pairs.quote==quote]
        self.symbols= df.symbol


    def Orders_excuted(self,history=1,symbol='BTC/USDT'):
            self.history=history
            self.symbol=symbol
            shift=self.history*60*60*1000
            exchange=ccxt.okex()
            exchange.load_markets()
            #symbol='BTC/USDT'
            if exchange.has['fetchTrades']:
              # for symbol in exchange.markets:  # ensure you have called loadMarkets() or load_markets() method.
                d=pd.DataFrame(exchange.fetch_trades (self.symbol,since=exchange.fetchTime(params = {})-shift))
            self.orders=d
            #return 
            
    def get_tweets(self):
              self.consumer_key='TM6AVxSu9Dt8VuzcFzbyF0MwB'
              self.consumer_secret='xUiJv2BxR8Aoax0qnd2ZT0fAgWBh35OfWZZ0Fnh5oMUys7NtWz'
            #'AAAAAAAAAAAAAAAAAAAAAEkgOAEAAAAAxPy0xM9uwViASjj5XvEfAuHp1m8%3DOGdajLXAze3Oq7rez1iUlYVyiX1rXQUJOEeIF6CTR4ZACrCG6g''
              self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
              self.auth.set_access_token('888817259342422016-wLATf1oBQ2BvlCES9T5slOatrJT1osy', 'smQOf65WtkMJohVr3TgdsR251TqAfgY4echPm082zFONW')
              self.data=[]
              api = tweepy.API(self.auth , wait_on_rate_limit=True)
              df_tweet=pd.DataFrame()
              public_tweets = api.home_timeline()
              public_tweets=api.user_timeline('@Whale_Alert',count =9000)
              userID='Whale_Alert'
              all_tweets = []
              tweets=api.user_timeline(screen_name=userID, 
                                        # 200 is the maximum allowed count
                                        count=300,
                                        include_rts = False,
                                
                                        # Necessary to keep full_text 
                                        # otherwise only the first 140 words are extracted
                                        tweet_mode = 'extended'
                                        )
              all_tweets.extend(tweets)
              oldest_id = tweets[-1].id
              while True:
                  tweets = api.user_timeline(screen_name=userID, 
                                        # 200 is the maximum allowed count
                                        count=300,
                                        include_rts = False,
                                        max_id = oldest_id - 1,
                                        # Necessary to keep full_text 
                                        # otherwise only the first 140 words are extracted
                                        tweet_mode = 'extended'
                                        )
                  if len(tweets) == 0:
                      break
                  oldest_id = tweets[-1].id
                  all_tweets.extend(tweets)
                  #print('N of tweets downloaded till now {}'.format(len(all_tweets)))

              data=[]
              for tweet in all_tweets:
                  #print(tweet.full_text)
                  text=tweet.full_text
                  time=tweet.created_at
                  #temp=tweettodf(text,time)
                  #if temp !=0:
                  self.tweettodf(text,time)
              for tweet in public_tweets:
                  #print(tweet.text)
                  text=tweet.text
                  time=tweet.created_at
                  self.tweettodf(text,time)
                  #if temp !=0:
                   # self.tweettodf(text,time)

              df_tweet=pd.DataFrame(self.data,columns=['time','coin_count','coin','amount_USD','source','destination'])


              df_tweet.coin_count=df_tweet.coin_count.apply(lambda x : x.replace(',','')).astype('int64')
              df_tweet.amount_USD=df_tweet.amount_USD.apply(lambda x : x.replace(',','')).astype('int64')
              df_tweet.sort_values('amount_USD',ascending=False)
              df_tweet.drop_duplicates(inplace=True)
              self.tweets=df_tweet
              return df_tweet 

    def tweettodf(self,text,time):

              a=re.split(" ",text)
              index=0
              for i, j in enumerate(a):

                try:
                  tmp = int(j.replace(',',''))
                  #print('The variable a number')
                  index=i
                except:
                  tmp=0
              a=a[index:]
            
              a[-1]=re.split("\n",a[-1])
              if len(a)>5:
                if ((a[1][0]=='#') & (a[4]=='transferred')):

                  coin_count=a[0]
                  symbol=a[1]
                  amount_USD=a[2][1:]
                  source=a[6]
                  destination=a[-1][0]
                  b=[time,coin_count,symbol,amount_USD,source,destination]
                  self.data.append(b)
                else:
                  return 0
              else:
                return 0
    def group_tweets(self,symbol='BTC',freq='1h'):
              df_tweet=self.tweets
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
              self.into=into
              self.outfrom=outfrom

'''    def plot_bokeh(self,into,outfrom,df):
              #into=self.into
              #outfrom=self.outfrom
              output_file("label.html", title="label.py example")
              z=outfrom.drop(['destination','source','amount_USD'],axis=1)
              z=z.reset_index()
              source = ColumnDataSource(data=z)
              df_ = df.copy()
              symbol=df['symbol'].unique()[0]
              inc = df_.Close > df_.Open
              dec = df_.Open > df_.Close
              #up=z.coin_price>z.Close
              #down=z.coin_price<z.Close
          
              w = 1*60*60*1000
              p = figure(x_axis_type="datetime", plot_width=1100, plot_height=500, title = symbol)
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


              #p.add_layout(labels)


              show(p)'''