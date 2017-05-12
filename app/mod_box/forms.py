from wtforms.fields.html5 import DateField
from app.queries import *
from flask_wtf import Form
from wtforms.fields import TextField, SubmitField, HiddenField, PasswordField, RadioField, BooleanField, SelectField,IntegerField
from wtforms.validators import Required


class Box(Form):
    alias = TextField("Box Alias",[Required()],)
    rows = IntegerField('Rows')
    columns = IntegerField('Columns')
    freezer = SelectField('Freezer')
    submit = SubmitField("Add Box")
    aliquots = RadioField("Aliquots Allowed?", choices=[(0, 'No'), (1, 'Yes')],default=0)

class Fill(Form):
    primer = SelectField('Primer')

    submit = SubmitField("Fill position with selected primer")


