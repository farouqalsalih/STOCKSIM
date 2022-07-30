from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, login_user, LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LocationForm, AddToCart
from forms import LoginForm
from foodnutritionapi import get_nutrition_data

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
app.config['SECRET_KEY'] = 'c2883c6f3a75f4135a2d0361c1ae3cb2'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
city = "New York"


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    cart = db.relationship("CartItems")


class CartItems(db.Model):
    __tablename__ = 'cart'
    itemid = db.Column(db.Integer, primary_key = True)
    itemname = db.Column(db.String(20), nullable = False)
    quanitity = db.Column(db.Integer, nullable = False)
    unit = db.Column(db.String(10), nullable = False)
    price = db.Column(db.Float, nullable = False)
    seller = db.Column(db.String(100), nullable = False)

    userid = db.Column(db.Integer, db.ForeignKey("user.id"))


class Store(db.Model):
    __tablename__ = 'store'
    storeid = db.Column(db.Integer, primary_key = True)
    storename = db.Column(db.String(50), nullable = False)
    storeaddress = db.Column(db.String(100), nullable = False)
    storelat = db.Column(db.Float, nullable = False)
    storelong = db.Column(db.Float, nullable = False)

    cart = db.relationship("Inventory")

class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventoryid = db.Column(db.Integer, primary_key = True)
    itemname = db.Column(db.String(20), nullable = False)
    price = db.Column(db.Float, nullable = False)
    unit = db.Column(db.String(10), nullable = False)

    storeid = db.Column(db.Integer, db.ForeignKey("store.storeid"))


def hardcode_locations():
    store1 = Store(storename = 'King Washington Grocery', storeaddress = '4225 Broadway, New York, NY 10033', storelat = 40.84918770614993, storelong = -73.93705621361732)
    


    store2 = Store(storename = 'Fine Fare Supermarkets', storeaddress = '4211 Broadway #17, New York, NY 10033', storelat = 40.84900104583396, storelong = -73.93820755183697)


    #store3 = Store(storename = 'La Parada Grocery', storeaddress = '706 W 177th St, New York, NY 10033', storelat = 40.84756226696742, storelong = -73.9385180265269)

    '''
    store4 = Store(storename = 'Rayira Grocery Deli corp.', storeaddress = '247 Audubon Ave, New York, NY 10033', storelat = 40.846230498563706, storelong = -73.93399715423584)

    store5 = Store(storename = 'Xcellente Supermarket', storeaddress = '1568 St Nicholas Ave, New York, NY 10040', storelat = 40.853881431557106, storelong = -73.93019378185272)

    store6 = Store(storename = 'Shop Fair Supermarket', storeaddress = '3871 Broadway, New York, NY 10032', storelat = 40.83692757377343, storelong = -73.94313197102434)
    '''
    db.session.add(store1)
    db.session.add(store2)
    #db.session.add(store3)
    '''
    db.session.add(store4)
    db.session.add(store5)
    db.session.add(store6)
    '''
    db.session.commit()

    store1inv1 = Inventory(itemname = "Apple", price = .99, unit = 'per', storeid = store1.storeid)
    store1inv2 = Inventory(itemname = "Pineapple", price = 4.99, unit = 'per', storeid = store1.storeid)
    db.session.add(store1inv1)
    db.session.add(store1inv2)

    store2inv1 = Inventory(itemname = "Grape", price = .25, unit = 'per', storeid = store2.storeid)
    store2inv2 = Inventory(itemname = "Cantelope", price = 3.99, unit = 'per', storeid = store2.storeid)
    db.session.add(store2inv1)
    db.session.add(store2inv2)

    db.session.commit()

db.create_all()
def get_locations():
    query = Store.query.all()
    return query

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    parent_html = "home.html"
    parent = "/home"
    home_loc_form = LocationForm()

    if home_loc_form.validate_on_submit():
        global city
        city = home_loc_form.city.data
        return redirect(url_for('main'))

    return render_template('location-form.html',
                           parent_html=parent_html, parent=parent,
                           loc_form=home_loc_form)


@app.route('/register', methods=['GET', 'POST'])
def register():

    
    parent_html = "register.html"
    parent = "/register"
    reg_form = RegistrationForm()

    # checks if entries are valid
    if reg_form.validate_on_submit():
        user = User.query.filter_by(name=reg_form.name.data).first()
        if user:
            flash("User already exist")
            return redirect(url_for('login'))
        password = request.form.get('password')
        user = User(name=reg_form.name.data,
                    email=reg_form.email.data,
                    address=reg_form.address.data,
                    password=generate_password_hash(password, method='sha256'))
        print(user)

        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {reg_form.name.data}!', 'success')

        # send to login page after registering account
        return redirect(url_for('login'))

    return render_template('location-form.html', title="Register",
                           parent_html=parent_html, parent=parent,
                           reg_form=reg_form)


# Flask_login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        # remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to
        # the hashed password in the database
        if user:
            # check the password
            if check_password_hash(user.password, password):
                # login_user(user)
                # want this to flash with the users Name
                flash("Log in Successful")
                global city
                address = user.address
            # if the user doesn't exist or password is wrong, reload the page
                login_user(user)
                return redirect(url_for('main'))
            else:
                flash("Wrong Password - Try again")
        else:
            flash("That user doesnt exist - Try again")
    return render_template('login.html', form=form)


# weather Stuff
@app.route('/main', methods=['GET', 'POST'])
def main():

    #hardcode_locations()
    store = get_locations()

    return render_template('main.html', stores = store)

@app.route('/mystore/<name>')
def profile(name):
    return 'hi' + name


@app.route('/store/<storename>', methods=['GET', 'POST'])
def storename(storename):
    form = AddToCart()
    print(Store.query.filter_by(storename = storename).first())
    query = Inventory.query.filter_by(storeid = Store.query.filter_by(storename = storename).first().storeid).all()
    store = Store.query.filter_by(storename = storename).first()
    print(query)

    if form.validate_on_submit():
        if current_user.is_authenticated:
            find = Inventory.query.filter_by(inventoryid = form.itemid).first()
            print(find)
            if CartItems.query.filter_by(itemname = find.itemname , userid = current_user.id).first() == None:
                newitem = CartItems(itemname = find.itemname, quanitity = form.amount.data, unit = find.unit, price = find.price, seller = Store.query.filter_by(storeid = find.storeid).first().storename, userid = current_user.id)
            else:
                newitem = CartItems(itemname = find.itemname, quanitity = (CartItems.query.filter_by(current_user.id).first().quantity + form.amount.data), unit = find.unit, price = find.price, seller = Store.query.filter_by(storeid = find.storeid).first().storename, userid = current_user.id)
            db.session.add(newitem)
            db.session.commit()
    return render_template('shop.html', shopinventory = query, store = store, form = form)

# this is to show the nutritional details for each food
@app.route('/nutritionaldetails/<foodname>', methods=['GET', 'POST'])
def foodnutrition(foodname):
    nutritionlist = get_nutrition_data(foodname)
    return render_template('nutritionaldetails.html', itemname = foodname, nutritionlist = nutritionlist)

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0")

# TODO set host = "0.0.0.0" instead of port 0
# TODO add logout