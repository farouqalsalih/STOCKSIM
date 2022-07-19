from optparse import Values
from tkinter.ttk import LabeledScale
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm
from stockinfo import getinfo, getlabels, getvalues


def getpopularstocks(stocklist):
    stocksinfo = []
    stocks = stocklist
    for stock in stocks:
        stockdict = {}
        priceaction = getvalues(stock, '1mo')

        trend = ''
        if priceaction[0] <= priceaction[len(priceaction) - 1]:
            trend = 'Up'
        else:
            trend = 'Down'
        
        percentchange = ((priceaction[len(priceaction) - 1] - priceaction[0]) / priceaction[0]) * 100
        pricechange = priceaction[len(priceaction) - 1] - priceaction[0]
        stockdict[stock] = {'Date' : getlabels(stock, '1mo'), 'Close' : getvalues(stock, '1mo'), 'Trend' : trend, 'PercentChange' : percentchange, 'PriceChange' : pricechange}
        stocksinfo.append(stockdict)
    return stocksinfo

app = Flask(__name__)

app.config['SECRET_KEY'] = '2c27df9a9141cf1529a88ca4da79adf3'

@app.route('/')
def index():
    index = getpopularstocks(['^IXIC', '^GSPC', '^DJI'])
    stocks = getpopularstocks(['NFLX', 'AAPL', 'AMC', 'GME'])
    return render_template('home.html', majorindexes = index, stocklists = stocks)

@app.route('/stocksearch.html', methods = ["POST", "GET"])
def search():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        print("hi")
        #flash(f"Search on {form.ticker.data} was successful!", 'success')
        ticker = form.ticker.data.upper()
        info = getinfo(ticker)
        
        labels = getlabels(ticker, '1mo')
        values = getvalues(ticker, '1mo')
        print(labels)
        print(values)

        return render_template('stocksearch.html', form = form, infodict = info, labels = labels, values = values)        
    
    return render_template('stocksearch.html', form = form)

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/home.html')
def home():
    index = getpopularstocks(['^IXIC', '^GSPC', '^DJI'])
    stocks = getpopularstocks(['NFLX', 'AAPL', 'AMC', 'GME'])
    return render_template('home.html', majorindexes = index, stocklists = stocks)

if __name__ == '__main__':
    app.run(port=0, debug = True)