# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 16:03:12 2018

@author: michal
"""

import zipfile
import sqlalchemy
import pandas as pd
import os

con = sqlalchemy.create_engine('mysql+pymysql://root:nasdaq93@127.0.0.1/hedge_fund') 

pairs = os.listdir('data/')

for pair in pairs:
    files = os.listdir('data/' + pair)
    for file in files:
        fileSplit = file.split('.')
        #unzip file
        zf = zipfile.ZipFile('data/' + pair + '/' + file, 'r')
        zf.extractall('data/' + pair + '/')
        zf.close()
        
        #read csv to dataframe
        df = pd.read_csv('data/' + pair + '/' + fileSplit[0] + '.csv', 
                         delimiter = ';', header = None)
                 
        #change column names
        df.columns = ['datetime','open','high','low','close','volume']
        
        #drop volume - non-informative variable
        df = df.drop('volume', axis = 1)
        
        #convert datetime column
        df['datetime'] = pd.to_datetime(df['datetime'], format = '%Y%m%d %H%M%S')
        df['source'] = 'histdata'
        
        #write to MySQL
        df.to_sql(con = con, name = pair, if_exists = 'append', index = False)
        
        #remove unzipe files
        os.remove('data/' + pair + '/' + fileSplit[0] + '.csv')
        os.remove('data/' + pair + '/' + fileSplit[0] + '.txt')

