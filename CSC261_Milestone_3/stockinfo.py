from multiprocessing.context import get_spawning_popen
from sqlite3 import Date
import yfinance as yf
import pandas as pd
from yahooquery import Ticker



def getinfo(ticker):
    tickerinfo = Ticker(ticker)
    return tickerinfo.summary_detail

def getinfoarray(tickers):
    dict = {}
    for ticker in tickers:
        tickerinfo = Ticker(ticker)
        print(ticker)
        dict[ticker] = tickerinfo.summary_detail
    return dict

def getlabels(ticker, timeperiod, timeinterval = '1d'):
    tickerinfo = yf.Ticker(ticker)
    data = tickerinfo.history(period = timeperiod, interval = timeinterval)
    data = data.reset_index(level=0)
    if 'index' in data:
        data.rename(columns={'index': 'Date'}, inplace=True)
    if 'Datetime' in data:
        data.rename(columns={'Datetime': 'Date'}, inplace=True)
    data['Date']= data['Date'].astype(str)
    return data['Date'].tolist()

def getvalues(ticker, timeperiod, timeinterval = '1d'):
    tickerinfo = yf.Ticker(ticker)
    data = tickerinfo.history(period = timeperiod, interval = timeinterval)
    
    return data['Close'].tolist()