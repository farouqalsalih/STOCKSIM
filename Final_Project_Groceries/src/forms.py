from cgi import print_exception
from curses import ALL_MOUSE_EVENTS
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField,
    FormField, DecimalField, IntegerField)
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LocationForm(FlaskForm):
    # latitude = DecimalField('Latitude', validators=[])

    # longitude = DecimalField('Longitude', validators=[])

    # szipcode = IntegerField('Zip', validators=[Length(max=5)])

    city = StringField('City', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired()])

    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    # location = FormField(LocationForm)
    address = StringField('Address', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Sign Up')


# Create Log in form
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddToCart(FlaskForm):
    amount = IntegerField('amount', validators=[DataRequired()])
    itemid = IntegerField('itemid ', validators=[DataRequired()])
    submit = SubmitField("Add To Cart")

class StoreRegistration(FlaskForm):
    storename = StringField('Store Name', validators=[DataRequired()])
    storeaddress = StringField('Store Address', validators=[DataRequired()])
    submit = SubmitField("Register your Store")

