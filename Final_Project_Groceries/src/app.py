from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, login_user, LoginManager, login_required, logout_user
from requests import delete
from werkzeug.security import generate_password_hash, check_password_hash
from forms import AddToInventory, RegistrationForm, LocationForm, AddToCart, StoreRegistration, AddToCart, DeleteFromInventory
from forms import LoginForm
from foodnutritionapi import get_nutrition_data
from geocode import getgeolocation
import haversine as hs 
from haversine import Unit
app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
app.config['SECRET_KEY'] = 'c2883c6f3a75f4135a2d0361c1ae3cb2'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

#pip install haversine

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    userlat = db.Column(db.Float, nullable = False)
    userlong = db.Column(db.Float, nullable = False)

    cart = db.relationship("CartItems")



class CartItems(db.Model):
    __tablename__ = 'cart'
    itemid = db.Column(db.Integer, primary_key = True)
    itemname = db.Column(db.String(20), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    unit = db.Column(db.String(10), nullable = False)
    price = db.Column(db.Float, nullable = False)
    seller = db.Column(db.String(100), nullable = False)

    userid = db.Column(db.Integer, db.ForeignKey("user.id"))


class Store(db.Model):
    __tablename__ = 'store'
    storeid = db.Column(db.Integer, primary_key = True)
    storename = db.Column(db.String(50), nullable = True)
    storeaddress = db.Column(db.String(100), nullable = True)
    storelat = db.Column(db.Float, nullable = True)
    storelong = db.Column(db.Float, nullable = True)
    storeowner = db.Column(db.String(20), nullable = True)

    cart = db.relationship("Inventory")
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))

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
        geolocationdata = getgeolocation(reg_form.address.data)
        user = User(name=reg_form.name.data,
                    email=reg_form.email.data,
                    address=reg_form.address.data,
                    password=generate_password_hash(password, method='sha256'), userlat = geolocationdata['lat'], userlong = geolocationdata['lon'])
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
    #TODO hard code locations when needed
    #hardcode_locations()
    store = get_locations()
    user = User.query.filter_by(id = current_user.id).first()
    userscart = CartItems.query.filter_by(userid = user.id).all()
    #gets subtotal
    subtotal = 0
    itemamount = 0
    for thing in userscart:
        itemamount += thing.quantity
        subtotal += thing.price * thing.quantity

    allinfo = {}
    distdict = {}
    for x in store:
        dist = hs.haversine((x.storelat, x.storelong), (user.userlat, user.userlong), unit=Unit.MILES)
        allinfo[x.storename] = {'storename' : x.storename, 'storeid' : x.storeid, 'storelat' : x.storelat, 
                                'storelong' : x.storelong, 'userid' : x.userid, 'distfromuser' : dist, 'storeaddress' : x.storeaddress}
        distdict[x.storename] = dist

    #this is a weird process that sorts the stores by how far they are so they can be put on the website in that order.
    sorted_values = sorted(distdict.values())
    sorted_dict = {}
    for i in sorted_values:
        for k in distdict.keys():
            if distdict[k] == i:
                sorted_dict[k] = distdict[k]
                break
    print(sorted_dict)

    return render_template('main.html', stores = store, allinfo = allinfo, sorted = sorted_dict, cart = userscart, subtotal = subtotal, itemamount = itemamount)



@app.route('/store/<storename>', methods=['GET', 'POST'])
def storename(storename):
    form = AddToCart()
    query = Inventory.query.filter_by(storeid = Store.query.filter_by(storename = storename).first().storeid).all()
    store = Store.query.filter_by(storename = storename).first()


    user = User.query.filter_by(id = current_user.id).first()
    userscart = CartItems.query.filter_by(userid = user.id).all()
    #gets subtotal
    subtotal = 0
    itemamount = 0
    for thing in userscart:
        itemamount += thing.quantity
        subtotal += thing.price * thing.quantity


    if form.validate_on_submit():
        if current_user.is_authenticated:
            find = Inventory.query.filter_by(inventoryid = form.itemid.data).first()
            print(find)
            if CartItems.query.filter_by(itemname = find.itemname , userid = current_user.id, seller = storename).first() == None:
                newitem = CartItems(itemname = find.itemname, quantity = form.amount.data, unit = find.unit, price = find.price, seller = Store.query.filter_by(storeid = find.storeid).first().storename, userid = current_user.id)
                db.session.add(newitem)
                db.session.commit()
            else:
                olditem = CartItems.query.filter_by(itemname = find.itemname , userid = current_user.id).first()
                olditem.quantity = olditem.quantity + form.amount.data
                db.session.commit()
        return redirect('/store/' + storename)
            
    return render_template('shop.html', shopinventory = query, store = store, form = form, cart = userscart, subtotal = subtotal, itemamount = itemamount)

# this is to show the nutritional details for each food
@app.route('/nutritionaldetails/<foodname>', methods=['GET', 'POST'])
def foodnutrition(foodname):
    nutritionlist = get_nutrition_data(foodname)
    return render_template('nutritionaldetails.html', itemname = foodname, nutritionlist = nutritionlist)

@app.route('/mystore/<name>', methods=['GET', 'POST'])
def profile(name):

    #### add guard against repeat items
    registerstore = StoreRegistration()
    additems = AddToInventory()
    deleteform = DeleteFromInventory()

    user = User.query.filter_by(id = current_user.id).first()
    userscart = CartItems.query.filter_by(userid = user.id).all()


    userstore = Store.query.filter_by(userid = current_user.id).first()
    userinv = Inventory.query.filter_by(storeid = Store.query.filter_by(storeid = userstore.storeid).first().storeid).all()
    
    #gets subtotal
    subtotal = 0
    itemamount = 0
    for thing in userscart:
        itemamount += thing.quantity
        subtotal += thing.price * thing.quantity


    if registerstore.validate_on_submit():
        geolocationdata = getgeolocation(registerstore.storeaddress.data)
        newstore = Store(storename = registerstore.storename.data, storeaddress = registerstore.storeaddress.data, 
                        storelat = geolocationdata['lat'], storelong = geolocationdata['lon'], storeowner = User.query.filter_by(id = current_user.id).first().name, userid = current_user.id)

        db.session.add(newstore)
        db.session.commit()
        return redirect('/mystore/' + name)
    
    if additems.validate_on_submit():
        newitem = Inventory(itemname = additems.itemname.data, price = additems.price.data, unit = additems.unit.data, storeid = Store.query.filter_by(userid = current_user.id).first().storeid)
        db.session.add(newitem)
        db.session.commit()
        return render_template('mystore.html', form = additems, cart = userscart, subtotal = subtotal, itemamount = itemamount, userinv = userinv, userstore = userstore, form1 = deleteform)


    if deleteform.validate_on_submit():
        item = Inventory.query.filter_by(inventoryid = deleteform.itemid.data).first()
        db.session.delete(item)
        db.session.commit()
        return render_template('mystore.html', form = additems, cart = userscart, subtotal = subtotal, itemamount = itemamount, userinv = userinv, userstore = userstore, form1 = deleteform)

    if Store.query.filter_by(userid = current_user.id).first() != None:
         return render_template('mystore.html', form = additems, cart = userscart, subtotal = subtotal, itemamount = itemamount, userinv = userinv, userstore = userstore, form1 = deleteform)
    else:
        return render_template('registerforshop.html', form = registerstore,  cart = userscart, subtotal = subtotal, itemamount = itemamount, userinv = userinv, userstore = userstore)
    
    

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0")

# TODO set host = "0.0.0.0" instead of port 0
# TODO add logout