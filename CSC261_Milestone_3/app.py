from flask import Flask, render_template, url_for, redirect
from sqlalchemy import false
from forms import RegistrationForm
from stockinfo import getinfo, getlabels, getvalues
from forms import LoginForm, RegistrationForm, StockSearchForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager, login_user, UserMixin, logout_user
import secrets

#this is boiler plate
app = Flask(__name__)

# hex token is required to use Flask Forms
app.config['SECRET_KEY'] = secrets.token_hex(16)


#takes a list of stocks, a time period and an interval and gets information from the api in a specific format
def getpopularstocks(stocklist, timeperiod, timeinterval = ''):
    stocksinfo = []
    stocks = set(stocklist)
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

#--------------------------------------------------------------------------------------------------------------------------#

# this is the base root, when the application is opened it will go to this route which is the sign up page
@app.route("/", methods=['GET', 'POST'])
def entrypage():
    form = RegistrationForm()
    if form.validate_on_submit(): 
        return redirect(url_for('signin')) 

    return render_template('register.html', title='Register', form=form)
    

@app.route('/signin.html', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    
    return render_template('signin.html', title="Login", form=form)
 

#gets the indexes and popular stock to show on home page and feeds the values into the front end
@app.route('/home.html')
def home():
    index = getpopularstocks(['^IXIC', '^GSPC', '^DJI'], '1d', '1m')
    ticker = ['NFLX', 'AAPL', 'AMC', 'GME']
    stocks = getpopularstocks(ticker, '1d', '1m')

    return render_template('home.html', majorindexes = index, stocklists = stocks)

#just the portfolio page
@app.route("/portfolio.html", methods = ["POST", "GET"])
def portfolio():
    return render_template("portfolio.html")


#this is also boiler plate
if __name__ == '__main__':
    app.run(debug = True, port = 0)