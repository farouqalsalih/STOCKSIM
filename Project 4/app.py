from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm
from stockinfo import getinfo

app = Flask(__name__)

app.config['SECRET_KEY'] = '2c27df9a9141cf1529a88ca4da79adf3'
random_list = [1 ,2 ,3 ,4 ,5, 69, 'end']

@app.route('/')
def index():
    return render_template('home.html', random = random_list)

@app.route('/stocksearch.html', methods = ["POST", "GET"])
def search():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        print("hi")
        #flash(f"Search on {form.ticker.data} was successful!", 'success')
        ticker = form.ticker.data.upper()
        info = getinfo(ticker)
        return render_template('stocksearch.html', form = form, infodict = info)        
    
    return render_template('stocksearch.html', form = form)

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/home.html')
def home():
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug = True)
