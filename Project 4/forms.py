from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    ticker = StringField('Ticker Symbol', validators=[DataRequired(), Length(min=1, max= 6)])
    submit = SubmitField('Search Ticker')
    