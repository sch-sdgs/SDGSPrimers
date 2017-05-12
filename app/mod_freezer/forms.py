from wtforms.fields.html5 import DateField
from app.queries import *
from flask_wtf import Form
from wtforms.fields import TextField, SubmitField, HiddenField, PasswordField, RadioField, BooleanField, SelectField,IntegerField
from wtforms.validators import Required


class Freezer(Form):
    name = TextField("Freezer Name")
    location = IntegerField('Location')

    submit = SubmitField("Add Freezer")

