#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 23:26:30 2018

@author: michal
"""

from datetime import datetime
import backtrader as bt
import pandas as pd
import sqlalchemy
import backtrader.indicators as btind
import matplotlib
import numpy as np

con = sqlalchemy.create_engine('mysql://root:nasdaq93@127.0.0.1/hedge_fund') 
data = pd.read_sql("select * from eurusd where datetime between '2016-01-11 09:00:00' and '2016-12-12 09:00:00'", con)
data0 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = -1)

class firstStrategy(bt.Strategy):
        
    def next(self):
        if str(self.data.datetime.time()) == "17:00:00":
            self.buy_bracket(price = self.data.close[0], limitprice = self.data.close[0] + 0.0005,
                             stopprice = self.data.close - 0.02, size = 1)
            self.buy_bracket(price = self.data.close[0], limitprice = self.data.close[0] - 0.0005,
                 stopprice = self.data.close + 0.02, size = 1)


cerebro = bt.Cerebro()
cerebro.addstrategy(firstStrategy)

cerebro.adddata(data0)

cerebro.run()
cerebro.plot(volume = False)
