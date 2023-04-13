from flask import Flask, render_template, url_for, redirect
from sqlalchemy import false
from forms import RegistrationForm
from stockinfo import getinfo, getlabels, getvalues, getinfoarray
from forms import LoginForm, RegistrationForm, StockSearchForm, BuyForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager, login_user, UserMixin, logout_user,login_required
import secrets
import mysql.connector
from login import signUp,validate
from user import *
import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Rg100356!",
  database = "STOCKSIM",
  autocommit = True
)

cursor = mydb.cursor()




#this is boiler plate
app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Rg100356!@localhost:3306/STOCKSIM"


db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    cash = db.Column(db.Float, nullable = False)
    phone_number = db.Column(db.String(10), nullable = False)
    user_password = db.Column(db.String(20), nullable=False)

    orders = db.relationship('Orders', backref='users', lazy=True)

    stats = db.relationship('Stats', backref='users', lazy=True)

    def get_id(self):
        return (self.user_id)

class Dividends(db.Model):
    ticker = db.Column(db.String(10), primary_key = True)
    payout = db.Column(db.Float)
    payment_date = db.Column(db.Date, primary_key = True)

    dividendpayout = db.relationship('Orders', backref='dividends', lazy=True)

class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key = True)
    buy = db.Column(db.Boolean, nullable = False)
    shares = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable = False)
    executed = db.Column(db.Boolean, nullable = False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    ticker = db.Column(db.String(10), db.ForeignKey('dividends.ticker'), nullable=False)
    
class Stats(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)
    instance_date = db.Column(db.Date, primary_key = True)
    user_rank = db.Column(db.Integer, nullable = False)
    portfolio_value = db.Column(db.Float, nullable = False)


class Portfolios(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key = True)
    ticker = db.Column(db.String(10), db.ForeignKey('dividends.ticker'), primary_key = True)
    shares = db.Column(db.Integer, nullable = False)


#db.create_all()


# hex token is required to use Flask Forms
app.config['SECRET_KEY'] = secrets.token_hex(16)





def giveDividends():
    today = datetime.date.today()
    cursor.execute("SELECT user_id FROM USERS")

    user_id_list = cursor.fetchall()

    for user_id in user_id_list:
        cursor.execute("SELECT ticker, shares FROM PORTFOLIOS WHERE PORTFOLIOS.user_id = " + str(user_id[0]))

        ticker_shares = cursor.fetchall()

        for tup in ticker_shares:
            ticker, shares = tup

            cursor.execute("SELECT payout FROM DIVIDENDS WHERE DIVIDENDS.ticker = '" + ticker + "' AND payment_date = '" + str(today) + "'")
            payout = cursor.fetchone()[0]
           

            updateCash(user_id[0], payout*shares)

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

def giveUserStock(user_id, ticker, shares):    
    cursor.execute("SELECT * FROM PORTFOLIOS WHERE PORTFOLIOS.user_id = " + str(user_id) + " and PORTFOLIOS.ticker = '" + ticker+"'")        
    if cursor.fetchone() == None:
        cursor.reset()
        cursor.execute("INSERT INTO PORTFOLIOS (user_id, ticker, shares) VALUES (" + str(user_id) + ", '" + ticker + "', " + str(shares) + ");")
    else:
        cursor.execute("UPDATE PORTFOLIOS SET PORTFOLIOS.shares = PORTFOLIOS.shares + " + str(shares) + " WHERE PORTFOLIOS.user_id = " + str(user_id) + " and PORTFOLIOS.ticker = '" + str(ticker)+"'")
     
def placeOrder(order_id, user_id, ticker, buying, shares, price):
    if buying:
        cursor.execute("SELECT SUM(price) FROM ORDERS WHERE ORDERS.buy = TRUE and ORDERS.user_id = " + str(user_id))
        tempUnavailable = cursor.fetchone()
        unavailableMoney = price
        if tempUnavailable != None and tempUnavailable[0] != None:
            unavailableMoney += tempUnavailable[0]             
        cursor.execute("SELECT cash FROM USERS WHERE USERS.user_id = " + str(user_id))
        availableMoney = cursor.fetchone()[0]
        if  availableMoney - unavailableMoney >= 0:        
            cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = FALSE and ORDERS.executed= FALSE and ORDERS.price <= " + str(price) + " and ORDERS.shares = " + str(shares) + " and ORDERS.ticker = '" + str(ticker)+"'")            
            if cursor.fetchone() == None:                
                cursor.reset()
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', TRUE, " + str(shares) + ", " + str(price) + ", FALSE);")
            else:                
                cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = FALSE and ORDERS.executed= FALSE and ORDERS.price = (SELECT MIN(price) FROM ORDERS) and ORDERS.shares = '" + str(shares) + "' and ORDERS.ticker = '" + str(ticker)+"'")
                cheapestSeller = cursor.fetchone()                
                updateCash(user_id, (-1)*cheapestSeller[5])
                giveUserStock(user_id, ticker, shares)
                giveUserStock(cheapestSeller[1], ticker, (-1)*shares)
                updateCash(cheapestSeller[1], cheapestSeller[5])
                cursor.execute("UPDATE ORDERS SET ORDERS.executed = TRUE WHERE ORDERS.order_id = " + str(cheapestSeller[0]))
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', True, " + str(shares) + ", " + str(price) + ", TRUE);")
    else:
        cursor.execute("SELECT SUM(shares) FROM ORDERS WHERE ORDERS.buy = FALSE and ORDERS.ticker = '" + ticker + "' and ORDERS.user_id = " + str(user_id))
        tempUnavShares = cursor.fetchone()
        unavailableShares = shares 
        if tempUnavShares != None and tempUnavShares[0] != None:
            unavailableShares += tempUnavShares[0]        
        cursor.execute("SELECT SUM(shares) FROM PORTFOLIOS WHERE PORTFOLIOS.ticker = '" + ticker + "' and PORTFOLIOS.user_id = " + str(user_id))
        tempTotal = cursor.fetchone()
        totalShares = 0
        if tempTotal != None and tempTotal[0] != None:
            totalShares = tempTotal[0]       
        if  totalShares - unavailableShares >= 0:
            cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = TRUE and ORDERS.executed = FALSE and ORDERS.price >= " + str(price) + " and ORDERS.shares = " + str(shares) + " and ORDERS.ticker = '" + ticker+"'")            
            if cursor.fetchone() == None:
                cursor.reset()
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', FALSE, " + str(shares) + ", " + str(price) + ", FALSE);")
            else:               
                cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = TRUE and ORDERS.executed = FALSE and ORDERS.price = (SELECT MAX(price) FROM ORDERS) and ORDERS.shares = " + str(shares) + " and ORDERS.ticker = '" + str(ticker) + "'")
                mostExpensiveBuyer = cursor.fetchone()
                updateCash(mostExpensiveBuyer[1], (-1)*mostExpensiveBuyer[5])
                updateCash(user_id, mostExpensiveBuyer[5])
                giveUserStock(mostExpensiveBuyer[1], ticker, shares)
                giveUserStock(user_id, ticker, (-1)*shares)
                cursor.execute("UPDATE ORDERS SET ORDERS.executed = TRUE WHERE ORDERS.order_id = " + str(mostExpensiveBuyer[0]))
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', FALSE, " + str(shares) + ", " + str(price) + ", TRUE);")
                            
def updateCash(user_id, ammount):
    cursor.execute("UPDATE USERS SET USERS.cash = USERS.cash + " + str(ammount) + "WHERE USERS.user_id = '" + str(user_id) + "'")
     
#--------------------------------------------------------------------------------------------------------------------------#



@login_manager.user_loader
def get_user(user_id):
  return Users.query.get(user_id)

# this is the base root, when the application is opened it will go to this route which is the sign up page
@app.route("/", methods=['GET', 'POST'])
def entrypage():

    form = RegistrationForm()
    if form.validate_on_submit(): 
        if current_user.is_authenticated == False:
            user = Users(user_id=form.username.data, email=form.email.data, first_name = form.firstname.data, last_name = form.lastname.data, cash = 10000, phone_number = form.phonenumber.data,user_password=form.password.data)
            db.session.add(user)
            db.session.commit()
            if form.firstname.data == "ADMIN":
                giveUserStock(form.username.data, "AZ", 10)
                giveUserStock(form.username.data, "BT", 10)
                giveUserStock(form.username.data, "CTC", 10)
                giveUserStock(form.username.data, "DHT", 10)
                giveUserStock(form.username.data, "EFG", 10)
                giveUserStock(form.username.data, "GIJ", 10)
                giveUserStock(form.username.data, "FLJ", 10)
                giveUserStock(form.username.data, "DEI", 10)
                giveUserStock(form.username.data, "FLK", 10)
                giveUserStock(form.username.data, "DXI", 10) 
            #signUp(form.username.data, form.email.data, form.firstname.data, form.lastname.data, form.phonenumber.data, 1000, form.password.data, mycursor)
            return redirect(url_for('signin')) 

    return render_template('register.html', title='Register', form=form, status = current_user.is_authenticated)
    

@app.route('/signin.html', methods=['GET', 'POST'])
def signin():
    
    form = LoginForm()
    if form.validate_on_submit():
        if current_user.is_authenticated == False:
            user = Users.query.filter_by(user_id = form.username.data, user_password = form.password.data).first()
            db = Users.query.all()
            if user != None:
                login_user(user)
                return redirect(url_for('home'))
            '''
            query = validate(form.username.data, form.password.data, mycursor)
            if query != None:
                user = Users(query)
                login_user(user)
                print(current_user.is_authenticated)
                print(current_user.__getitem__)
                return redirect(url_for('home'))
            '''
    return render_template('signin.html', title="Login", form=form, status = current_user.is_authenticated)
 

#gets the indexes and popular stock to show on home page and feeds the values into the front end
@login_required
@app.route('/home.html', methods = ["POST", "GET"])
def home():
    if current_user.is_authenticated:
        form = StockSearchForm()
        if form.validate_on_submit():
            tickersymbol = form.ticker.data.upper()
            try:
                getpopularstocks([tickersymbol], "1d", "1m")
                return redirect(url_for('ticker', ticker=tickersymbol))
            except:
                return redirect(url_for("home"))

        
        index = getpopularstocks(['^IXIC', '^GSPC', '^DJI'], '1d', '1m')
        ticker = ['NFLX', 'AAPL', 'AMC', 'GME']
        stocks = getpopularstocks(ticker, '1d', '1m')

        return render_template('home.html', majorindexes = index, stocklists = stocks, stocksinfo = getinfoarray(ticker), form = form)
    else:
        return redirect(url_for("signin"))

#just the portfolio page
@app.route("/portfolio.html", methods = ["POST", "GET"])
def portfolio():
    if current_user.is_authenticated:
         cash = Users.query.filter_by(user_id = current_user.user_id).first().cash

         positions = Portfolios.query.filter_by(user_id = current_user.user_id).all()

         transactions = Orders.query.filter_by(user_id = current_user.user_id, executed = True ).all()
         return render_template("portfolio.html", cash = cash, positions = positions, transactions = transactions)
    
    else:
        return redirect(url_for("signin"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('entrypage'))


@app.route("/tradestock.html",  methods=['GET', 'POST'])
def tradestock():
    if current_user.is_authenticated:
        form = BuyForm()
        if form.validate_on_submit():
            
            ordernum = len(Orders.query.all()) + 1
            placeOrder(ordernum, current_user.user_id, form.stock.data, form.buy.data, form.quantity.data, form.price.data)


        return render_template("tradestock.html", form = form)
    else:
        return redirect(url_for("signin"))

@app.route("/leaderboard.html")
def leaderboard():
    if current_user.is_authenticated:
        users = Users.query.order_by(Users.cash).all()

        cursor.execute("DELETE FROM STATS;")
        print(users[-1].cash)
        rank = 1
        for i in range(len(users) - 1, -1, -1):
            newstat = Stats(user_id = users[i].user_id, instance_date = datetime.datetime.now().strftime('%Y-%m-%d'), user_rank = rank, portfolio_value = users[i].cash)
            db.session.add(newstat)
            db.session.commit()
            rank += 1
        usersrank = Stats.query.all()
        return render_template("leaderboard.html", usersrank = usersrank)
    else:
        return redirect(url_for("signin"))

scheduler = BackgroundScheduler()
job = scheduler.add_job(giveDividends, 'cron', day_of_week ='mon-sun', hour=0, minute=0)
scheduler.start()

#this is also boiler plate
if __name__ == '__main__':
    app.run(debug = True, port = 0)