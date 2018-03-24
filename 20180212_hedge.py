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

file = open('logi.csv', 'w')
file.write("Type;Price;Size;Value;Commision;K;K_1;D;D_1;RSI;WILLIAMS\n")

class StrategyStochastic(bt.Strategy):           
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data0.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]: 
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.5f, Size: %.2f, Cost: %.2f, Comm %.2f, K %.2f, K_1 %.2f, D %.2f, D_1 %.2f' %
                        (order.executed.price,
                         order.executed.size,
                         order.executed.value,
                         order.executed.comm,
                         self.stoch.slowk[-1],
                         self.stoch.slowk[-2],
                         self.stoch.slowd[-1],
                         self.stoch.slowd[-2]))
                line = ("BUY; " + str(order.executed.price) + ";" + str(order.executed.size) + 
                           ";" + str(order.executed.value) + ";" + str(order.executed.comm) + 
                           ";" + str(self.stoch.slowk[-1]) + ";" + str(self.stoch.slowk[-2]) +
                           ";" + str(self.stoch.slowd[-1]) + ";" + str(self.stoch.slowd[-2]) +
                           ";" + str(self.rsi[0]) + ";" + str(self.williams[0]))
                file.write(line)
                file.write('\n')
                
            else:  # Sell
                self.log('SELL EXECUTED, ID: %.2f, Price: %.5f, Size: %.2f, Cost: %.2f, Comm %.2f, K %.2f, K_1 %.2f, D %.2f, D_1 %.2f' %
                         (order.tradeid,
                          order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm,
                         self.stoch.slowk[-1],
                         self.stoch.slowk[-2],
                         self.stoch.slowd[-1],
                         self.stoch.slowd[-2]))
                line = ("SELL; " + str(order.executed.price) + ";" + str(order.executed.size) + 
                           ";" + str(order.executed.value) + ";" + str(order.executed.comm) + 
                           ";" + str(self.stoch.slowk[-1]) + ";" + str(self.stoch.slowk[-2]) +
                           ";" + str(self.stoch.slowd[-1]) + ";" + str(self.stoch.slowd[-2]) +
                           ";" + str(self.rsi[0]) + ";" + str(self.williams[0]))
                file.write(line)
                file.write('\n')
        # Sentinel to None: new orders allowed
        self.order = None        
 
        
    def __init__(self):
        self.williams = bt.talib.WILLR(self.data2.high, self.data2.low, self.data2.close)
        self.rsi = bt.indicators.RSI(self.data1.close, period=14)
        self.stoch = bt.talib.STOCH(self.data0.high, self.data0.low, self.data0.close,
                                   fastk_period=10, slowk_period=3, slowd_period=3)
        
    def next(self):
        if not self.position:
            self.stoch.slowk
            if self.stoch.slowk[-1] < self.stoch.slowd[-1] and\
                self.stoch.slowk[0] >= self.stoch.slowd[0] and\
                self.stoch.slowk[0] < 30 and\
                (self.rsi[0] < 70 or self.williams[0] > -20):
                    self.buy(size=100)
        else:
            if self.stoch.slowk[-1] >= self.stoch.slowd[-1] and\
                self.stoch.slowk[0] < self.stoch.slowd[0] and\
                self.stoch.slowk[0] > 70 and\
                (self.rsi[0] > 30 or self.williams[0] < -80):
                    self.sell(size=100)


cerebro = bt.Cerebro()
cerebro.addstrategy(StrategyStochastic)
        
con = sqlalchemy.create_engine('mysql://root:nasdaq93@127.0.0.1/hedge_fund') 

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 60);", con)

data0 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 1440);", con)

data1 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 240);", con)

data2 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)


cerebro.adddata(data0)
cerebro.adddata(data1)
cerebro.adddata(data2)

cerebro.run()
cerebro.plot(volume = False)
file.close()