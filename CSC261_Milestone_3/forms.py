from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class StockSearchForm(FlaskForm):
    ticker = StringField('', validators=[DataRequired(), Length(min=1, max= 6)])
    submit = SubmitField('Search Ticker')

class RegistrationForm(FlaskForm):
    username = IntegerField('Student ID',
                           validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    firstname = StringField("Firstname", validators = [DataRequired()])
    lastname = StringField("Lastname", validators = [DataRequired()])
    phonenumber = StringField("Phone #", validators= [DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BuyForm(FlaskForm):
    stock  = StringField("Stock Ticker", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    buy = BooleanField('Are you buying?')
    price = IntegerField("What price do you want to buy it at", validators=[DataRequired()])
    submits = SubmitField("Trade")