from optparse import Values
from tkinter.ttk import LabeledScale
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm
from stockinfo import getinfo, getlabels, getvalues
from newsdata import getnews

'''
y finance, flask, flask wtf, newsdataapi, these are the required imports
'''

def getpopularstocks(stocklist, timeperiod, timeinterval = ''):
    stocksinfo = []
    stocks = stocklist
    for stock in stocks:
        stockdict = {}
        priceaction = getvalues(stock, timeperiod, timeinterval)

        trend = ''
        if priceaction[0] <= priceaction[len(priceaction) - 1]:
            trend = 'Up'
        else:
            trend = 'Down'
        
        percentchange = ((priceaction[len(priceaction) - 1] - priceaction[0]) / priceaction[0]) * 100
        pricechange = priceaction[len(priceaction) - 1] - priceaction[0]
        stockdict[stock] = {'Date' : getlabels(stock, timeperiod, timeinterval), 'Close' : getvalues(stock, timeperiod, timeinterval), 'Trend' : trend, 'PercentChange' : percentchange, 'PriceChange' : pricechange}
        stocksinfo.append(stockdict)
    return stocksinfo

app = Flask(__name__)

app.config['SECRET_KEY'] = '2c27df9a9141cf1529a88ca4da79adf3'

@app.route('/')
def index():
    index = getpopularstocks(['^IXIC', '^GSPC', '^DJI'], '1d', '1m')
    stocks = getpopularstocks(['NFLX', 'AAPL', 'AMC', 'GME'], '1d', '1m')
    news = getnews()
    return render_template('home.html', majorindexes = index, stocklists = stocks, stocknews = news)

@app.route('/stocksearch.html', methods = ["POST", "GET"])
def search():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        print("hi")
        #flash(f"Search on {form.ticker.data} was successful!", 'success')
        ticker = form.ticker.data.upper()
        info = getinfo(ticker)

        #TODO: Add time span and interval

        labels = getlabels(ticker, '1mo')
        values = getvalues(ticker, '1mo')

        trend = ''
        if values[0] <= values[len(values) - 1]:
            trend = 'Up'
        else:
            trend = 'Down'
        
        percentchange = ((values[len(values) - 1] - values[0]) / values[0]) * 100
        pricechange = values[len(values) - 1] - values[0]

        return render_template('stocksearch.html', form = form, infodict = info, labels = labels, values = values, 
                                trend = trend, percentchange = percentchange, pricechange = pricechange)        
    
    return render_template('stocksearch.html', form = form)

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/home.html')
def home():
    index = getpopularstocks(['^IXIC', '^GSPC', '^DJI'], '1d', '1m')
    stocks = getpopularstocks(['NFLX', 'AAPL', 'AMC', 'GME'], '1d', '1m')
    news = getnews()
    return render_template('home.html', majorindexes = index, stocklists = stocks, stocknews = news)

if __name__ == '__main__':
    app.run(port=0, debug = True)