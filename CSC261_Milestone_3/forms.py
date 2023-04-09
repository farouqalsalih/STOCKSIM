from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class StockSearchForm(FlaskForm):
    ticker = StringField('Ticker Symbol', validators=[DataRequired(), Length(min=1, max= 6)])
    timeperiod = SelectField(u'Time Period', choices = [('1d', '1d'), ('5d', '5d'), ('1mo', '1mo'), ('3mo', '3mo'), ('6mo', '6mo'), ('1y', '1y'), ('2y', '2y'), ('5y', '5y'), ('10y', '10y'), ('max', 'max')])
    timeinterval = SelectField(u'Time Interval', choices = [('1m', '1m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'), ('1h', '1h'), ('1d', '1d'), ('1mo', '1mo')])
    submit = SubmitField('Search Ticker')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
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
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

