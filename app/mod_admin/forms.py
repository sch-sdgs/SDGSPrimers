from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import TextField, SubmitField, HiddenField, BooleanField, SelectMultipleField
from wtforms.validators import Required
from app.models import *
from app.primers import s
from app.models import *


def users():
    return s.query(Users)

class UserRoleForm(Form):
    role = TextField("Role",  [Required("Enter a Username")])
    submit = SubmitField("Add Role")

class UserForm(Form):
    username = TextField("User Name", [Required("Enter a Username")])
    firstname = TextField("First Name", [Required("Enter a Username")])
    surname = TextField("Surname", [Required("Enter a Username")])
    email = TextField("Email", [Required("Enter a Username")])
    staff_no = TextField("Staff Number", [Required("Enter a Username")])
    userrole = QuerySelectMultipleField("User Role", query_factory=lambda: s.query(UserRolesRef).all(), get_label="role")
    submit = SubmitField()


class UserEditForm(Form):
    username = TextField("User Name", [Required("Enter a Username")])
    firstname = TextField("First Name", [Required("Enter a Username")])
    surname = TextField("Surname", [Required("Enter a Username")])
    email = TextField("Email", [Required("Enter a Username")])
    staff_no = TextField("Staff Number", [Required("Enter a Username")])
    userrole = SelectMultipleField("User Role")
    submit = SubmitField()

class ApplicationsForm(Form):
    name = TextField("Application", [Required("Enter an Application")])
    paired = BooleanField("Paired Primers?")
    submit = SubmitField("Add Application")