# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 11:41:09 2018


"""

import requests
import pandas as pd
from pandas_datareader import data as web
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup
import datetime as dt
from datetime import timedelta, time
from time import sleep
import sqlite3
import time
import json
import schedule   #import schedule library to automatically update database
def load_daily_data():
    stocklist=['MSFT','GOOG','TSLA']
    for ticker in stocklist:
        daily_url="https://query1.finance.yahoo.com/v8/finance/chart/%s?region=US&lang=en-US&includePrePost=false&interval=2m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance" %(ticker)
        # load data to table "daily"
        response = requests.get(daily_url)
        js= response.json()
        
        daily_time = js["chart"]["result"][0]["timestamp"]
        strlist = js['chart']['result'][0]['indicators']['quote'][0]

        for i in range(0, len(daily_time)):
            try:
                current_time = daily_time[i]
#                print(current_time)
                minute_open= round(strlist["open"][i],2)
                minute_close = round(strlist["close"][i],2)
                minute_high = round(strlist["high"][i],2)
                minute_low = round(strlist["low"][i],2)
                minute_volume= strlist["volume"][i]
                timeArray = time.localtime(current_time)
                day = time.strftime("%y-%m-%d", timeArray)
#                print(day)
                hour = time.strftime('%H:%M', timeArray)
#                print(hour)
#                c.execute('''INSERT INTO dailydata VALUES(?,?,?,?,?,?,?,?,?)''',
#                            (ticker, current_time,minute_open,minute_close,minute_high,minute_low, minute_volume,day,hour))
#            except:
#                pass
                # check whether the record has alreadly existed
                c.execute('''SELECT * FROM dailydata WHERE stock = '%s'AND time= '%s' ''' % (ticker, current_time))
                b=list(c.fetchall())
                if not b:
                    c.execute('''INSERT INTO dailydata VALUES(?,?,?,?,?,?,?,?,?)''',
                        (ticker, current_time,minute_open,minute_close,minute_high,minute_low, minute_volume,day,hour))
                    
            except:
                pass
            
            conn.commit()
    c.execute('SELECT count(*) FROM dailydata')
    print(*c.fetchall(), sep='\n') 
def load_historical_data():
    stocklist=['MSFT','GOOG','TSLA']
    for ticker in stocklist:
        historical_url ="https://finance.yahoo.com/quote/%s/history?p=%s"%(ticker, ticker)
        response= requests.get(historical_url)
        strlist = response.text.split('"HistoricalPriceStore":{"prices":')
        for item in strlist[1:]:
            try:
                list_link = item.split(',"isPending"')[0]       
            except:
                pass

        list_link=json.loads(list_link)
        datalist=[]
        for line in list_link:
    
            try:
                date=line["date"]
                open_=round(line["open"],2)
                high=round(line["high"],2)
                low=round(line["low"],2)
                close=round(line["close"],2)
                volume=line["volume"]
                adjclose=round(line["adjclose"],2)
                timeStamp = line["date"]
                timeArray = time.localtime(timeStamp)
                month = time.strftime("%m", timeArray)
                year = time.strftime("%y", timeArray)
                date_new = time.strftime("%m/%d", timeArray)
#                print otherStyleTime   # 2013--10--10 23:40:00
                data=(ticker, date,high,low,open_,close,volume,adjclose,month,year,date_new)
#                datalist.append(data)
#                c.execute('''SELECT * FROM historicaldata  WHERE stock = '%s'AND date= '%s' ''' % (ticker, date))
#                b =list(c.fetchall())
#                if not b:
                c.execute('''insert into historicaldata values (?,?,?,?,?,?,?,?,?,?,?)''', data)
            except:
                pass
  #      conn.executemany('''insert into historicaldata values (?,?,?,?,?,?,?,?,?,?,?)''', datalist)
        conn.commit()
           

conn = sqlite3.connect('stock.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS historicaldata(stock TEXT, date INT, high REAL, low REAL, open REAL, 
            close REAL, volume INT, adj_close REAl, month INT, year INT,date_new TEXT)
        ''')
c.execute('''CREATE TABLE IF NOT EXISTS dailydata(stock TEXT, time INT, open FLOAT, close FLOAT,
            high Float, low Float, volume INT,day TEXT, hour TEXT)
        ''')

conn.commit()


#c.execute('drop table dailydata ')
#c.execute('''CREATE TABLE IF NOT EXISTS dailydata(stock TEXT, time INT, open FLOAT, close FLOAT,
#            high Float, low Float, volume INT)
#        ''')
#load_daily_data()
#c.execute('SELECT count(*) FROM dailydata')
#c.execute('SELECT * FROM dailydata')
#print(*c.fetchall(), sep='\n') 
c.execute('drop table historicaldata ')
c.execute('''CREATE TABLE IF NOT EXISTS historicaldata(stock TEXT, date INT, high REAL, low REAL, open REAL, 
            close REAL, volume INT, adj_close REAl, month INT, year INT,date_new TEXT)
        ''')
load_historical_data()
#c.execute('SELECT count(*) FROM historicaldata')
#c.execute('SELECT * FROM historicaldata')
#print(*c.fetchall(), sep='\n') 

conn.commit()

schedule.every(1).minutes.do(load_daily_data)

while True:
    schedule.run_pending()
    time.sleep(1)
    
conn.close()

