from flask import Flask, render_template, url_for

app = Flask(__name__)
random_list = [1 ,2 ,3 ,4 ,5, 69, 'end']

@app.route('/')
def index():
    return render_template('home.html', random = random_list)

@app.route('/stocksearch.html')
def search():
    return render_template('stocksearch.html')

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
