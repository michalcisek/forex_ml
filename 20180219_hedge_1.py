#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 18:56:21 2018

@author: michal
"""

from datetime import datetime
import backtrader as bt
import pandas as pd
import sqlalchemy
import backtrader.indicators as btind
import matplotlib
import numpy as np
import talib

class StrategyTime(bt.Strategy):           
    def __init__(self):
        self.atr = bt.talib.ATR(self.data1.high, self.data1.low,
                                     self.data1.close, timeperiod = 14)
        self.mean_atr = bt.talib.SMA(self.atr, timeperiod = 20)
    def next(self):
        time = str(self.datetime.time(ago = 0))
        print(time)
        if (time == "22:30:00" and (self.atr[0] < self.mean_atr[0])):
            self.buy(size=100)


cerebro = bt.Cerebro()
cerebro.addstrategy(StrategyTime)
        
con = sqlalchemy.create_engine('mysql://root:nasdaq93@127.0.0.1/hedge_fund') 

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 30);", con)

data0 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 1440);", con)

data1 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)


cerebro.adddata(data0)
cerebro.adddata(data1)

cerebro.run()
cerebro.plot(volume = False)