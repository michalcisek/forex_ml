#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 17:59:32 2018

@author: michal
"""

from datetime import datetime
import backtrader as bt
import pandas as pd
import sqlalchemy
import backtrader.indicators as btind
import matplotlib
import numpy as np

class firstStrategy(bt.Strategy):

    def notify_order(self, order):
        if order.status != order.Completed:q
            return

        self.order = None
        print('{} {} {} Executed at price {}'.format(
            bt.num2date(order.executed.dt).date(),
            bt.num2time(order.executed.dt),
            'Buy' * order.isbuy() or 'Sell', order.executed.price)
        )
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        self.sma = bt.indicators.SMA(self.data.close, period=30)        
    def next(self):
        if not self.position:
            if self.rsi[-1] < 50 and self.rsi[0] >= 50:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)
        
cerebro = bt.Cerebro()
cerebro.addstrategy(firstStrategy)
        
con = sqlalchemy.create_engine('mysql+pymysql://root:nasdaq93@127.0.0.1/hedge_fund') 

data = pd.read_sql("call change_timeframe('eurusd', '2015-01-01', '2015-12-31', 15);", con)

data = pd.read_sql("""select DATE(datetime) as date, MAX(high) as high, MIN(low) as low  
                   from eurusd where YEAR(datetime) between 2014 and 2016 group by DATE(datetime);""", con)

data1 = pd.read_sql("""select DATE(datetime) as date, open from eurusd where datetime in (
                    select MIN(datetime)  
                   from eurusd 
                   where YEAR(datetime) between 2014 and 2016 
                   group by DATE(datetime));""", con)

data2 = pd.read_sql("""select DATE(datetime) as date, close from eurusd where datetime in (
                    select MAX(datetime)  
                   from eurusd 
                   where YEAR(datetime) between 2014 and 2016
                   group by DATE(datetime));""", con)
data3 = data1.set_index('date').join(data.set_index('date')).join(data2.set_index('date'))
data3['datetime'] = data3.index.to_datetime()
data3 = data3.sort_values(by='datetime')

data0 = bt.feeds.PandasData(dataname = data3, openinterest = None, datetime = 4, 
                            open = 0, high = 1, low = 2, close = 3, volume = None)

data = pd.read_sql("select * from eurusd where datetime between '2014-01-11 09:00:00' and '2016-01-11 12:00:00'", con)
data0 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = -1)

cerebro.adddata(data0)

cerebro.run()
cerebro.plot(volume = False)

