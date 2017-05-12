from wtforms.fields.html5 import DateField
from app.queries import *
from flask_wtf import Form
from wtforms.fields import TextField, SubmitField, HiddenField, PasswordField, RadioField, BooleanField, SelectField,IntegerField
from wtforms.validators import Required

class Add(Form):
    name = TextField("Set Name")
    submit = SubmitField("Add Set")

class Choose(Form):
    set = SelectField("Set")
    submit = SubmitField("Choose Set")