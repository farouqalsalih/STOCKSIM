import yfinance as yf

def getinfo(ticker):
    tickerinfo = yf.Ticker(ticker)
    return tickerinfo.info