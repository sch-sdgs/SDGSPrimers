from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import TextField, SubmitField, HiddenField, BooleanField
from wtforms.validators import Required

from app.primers import s
from app.models import *


def users():
    return s.query(Users)

class UserForm(Form):
    name = TextField("Username",  [Required("Enter a Username")])
    admin = BooleanField("Admin")
    submit = SubmitField("Add User")

class ApplicationsForm(Form):
    name = TextField("Application", [Required("Enter an Application")])
    paired = BooleanField("Paired Primers?")
    submit = SubmitField("Add Application")