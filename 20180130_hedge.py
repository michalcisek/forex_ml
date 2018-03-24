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

file = open('logi.csv', 'w')
file.write("Type;Price;Size;Value;Commision;RSI;RSI_1\n")


class OrderObserver(bt.observer.Observer):
    lines = ('created', 'expired',)

    plotinfo = dict(plot=True, subplot=True, plotlinelabels=True)

    plotlines = dict(
        created=dict(marker='*', markersize=8.0, color='lime', fillstyle='full'),
        expired=dict(marker='s', markersize=8.0, color='red', fillstyle='full')
    )

    def next(self):
        for order in self._owner._orderspending:
            if order.data is not self.data:
                continue

            if not order.isbuy():
                continue

            # Only interested in "buy" orders, because the sell orders
            # in the strategy are Market orders and will be immediately
            # executed

            if order.status in [bt.Order.Accepted, bt.Order.Submitted]:
                self.lines.created[0] = order.created.price
                print(self._owner.broker.getcash())
            elif order.status in [bt.Order.Expired]:
                self.lines.expired[0] = order.created.price

class firstStrategy(bt.Strategy):        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
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
                self.log('BUY EXECUTED, Price: %.5f, Size: %.2f, Cost: %.2f, Comm %.2f, RSI %.2f, RSI_1 %.2f' %
                        (order.executed.price,
                         order.executed.size,
                         order.executed.value,
                         order.executed.comm,
                         self.rsi[-1],
                         self.rsi[-2]))
                line = ("BUY; " + str(order.executed.price) + ";" + str(order.executed.size) + 
                           ";" + str(order.executed.value) + ";" + str(order.executed.comm) + 
                           ";" + str(self.rsi[-1]) + ";" + str(self.rsi[-2]))
                file.write(line)
                file.write('\n')
                
            else:  # Sell
                self.log('SELL EXECUTED, ID: %.2f, Price: %.5f, Size: %.2f, Cost: %.2f, Comm %.2f, RSI %.2f, RSI_1 %.2f' %
                         (order.tradeid,
                          order.executed.price,
                          order.executed.size,
                          order.executed.value,
                          order.executed.comm,
                          self.rsi[-1],
                          self.rsi[-2]))
                line = ("SELL; " + str(order.executed.price) + ";" + str(order.executed.size) + 
                           ";" + str(order.executed.value) + ";" + str(order.executed.comm) + 
                           ";" + str(self.rsi[-1]) + ";" + str(self.rsi[-2]))
                file.write(line)
                file.write('\n')
        # Sentinel to None: new orders allowed
        self.order = None        
        
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
cerebro.addobserver(OrderObserver)
cerebro.addstrategy(firstStrategy)
        
con = sqlalchemy.create_engine('mysql://root:nasdaq93@127.0.0.1/hedge_fund') 

data = pd.read_sql("call change_timeframe('eurusd', '2015-03-01', '2015-05-31', 60);", con)

data0 = bt.feeds.PandasData(dataname = data, openinterest = None, datetime = 0, 
                            open = 2, high = 3, low = 4, close = 5, volume = None)

cerebro.adddata(data0)

cerebro.run()
cerebro.plot(volume = False)
file.close()
