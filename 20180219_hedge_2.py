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
        self.hammer = bt.talib.CDLHAMMER(self.data0.open, self.data0.high,
                                        self.data0.low, self.data0.close)
        self.shooting_star = bt.talib.CDLSHOOTINGSTAR(self.data0.open, self.data0.high,
                                 self.data0.low, self.data0.close)
        
        self.difference = self.data0.close - self.data0.open
    def next(self):
        
        if (self.hammer[-1] == 100 and self.difference[0] >= 0.001):
            self.buy(size = 100)
            print(self.difference[0])
        if (self.shooting_star[-1] == -100 and self.difference[0] <= -0.001):
            self.sell(size = 100)
            print(self.difference[0])
            

cerebro = bt.Cerebro()
cerebro.addstrategy(StrategyTime)
        
con = sqlalchemy.create_engine('mysql://root:nasdaq93@127.0.0.1/hedge_fund') 

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 60);", con)

data0 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)

cerebro.adddata(data0)

cerebro.run()
cerebro.plot(plotabove = True)
cerebro.plot(volume = False, style = "candle", barupfill = False, 
             bardownfill = "black", bardown = "black", barup = "black")






