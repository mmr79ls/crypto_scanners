
import pandas as pd
import numpy as np

def BTC_drop_change(OHLCV,start,end,change_low,change_high):    
            filtered=OHLCV[(OHLCV['Date'] >= start) & (OHLCV['Date'] <= end)]
            OHLCV_change=filtered[(filtered['change']>=change_low) & (filtered['change']<=change_high)].sort_values('change')
            return OHLCV_change

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
          
            
def df_adjust_step(df_bid_ex,df_ask_ex,quote,step_percentage,prices):      
         df_bid_adjusted=pd.DataFrame()
         df_ask_adjusted=pd.DataFrame()
         symbols=df_bid_ex.symbol.unique()
         print(symbols)
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
                            df_bid=df_bid.groupby(pd.cut(df_bid["bid"], np.arange(mins, maxs+step, step))).agg({'amount':'sum','bid':'mean','amount_BTC':sum,'amount_USDT':sum})
                            df_bid['price']=df_bid.index
                        df_bid['symbol']=symbol
                        
                        df_bid_adjusted=pd.concat([df_bid,df_bid_adjusted],ignore_index=True)
         symbols=df_ask_ex.symbol.unique()                   
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
                            df_ask=df_ask.groupby(pd.cut(df_ask["ask"], np.arange(mins, maxs+step, step))).agg({'amount':'sum','ask':'mean','amount_BTC':sum,'amount_USDT':sum})
                            df_ask['price']=df_ask.index
                        df_ask['symbol']=symbol
                        df_ask_adjusted=pd.concat([df_ask,df_ask_adjusted],ignore_index=True)
                        
         return df_bid_adjusted,df_ask_adjusted       
     
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