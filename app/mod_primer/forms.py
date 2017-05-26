from wtforms.fields.html5 import DateField
from app.queries import *
from flask_wtf import Form
from wtforms.fields import TextField, SubmitField, HiddenField, PasswordField, RadioField, BooleanField, SelectField, TextAreaField
from wtforms.validators import Required
import datetime


class Primer(Form):
    alias = TextField("Primer Alias",validators=[Required()])
    sequence = TextField("Sequence")

    application = SelectField('Application')

    m13 = BooleanField('Add M13 Tag?')

    orientation = RadioField('Orientation', choices=[(0, 'F'), (1, 'R')])

    dt = DateField('Date Designed',
                   format='%Y-%m-%d', default=datetime.date.today)
    purification = SelectField(label='Purification',
                               choices=[("Standard Desalting", "Standard Desalting"), ("PAGE Purification", "PAGE"),
                                        ("HPLC Purification", "HPLC"), ("IE HPLC Purification", "IE HPLC"),
                                        ("Dual HPLC Purification", "Dual HPLC"),
                                        ("RNase-Free HPLC Purification", "RNase-Free HPLC")])
    mod_5 = SelectField(label="5' Modification",
                        choices=[("None", "None"), ("/5HEX/", "/5HEX/")])
    mod_3 = SelectField(label="3' Modification",
                        choices=[("None", "None")])

    scale = SelectField(label="Scale",
                        choices=[("None", "None"), ("25nmole DNA Oligo", "25nmole DNA Oligo"),
                                 ("100nmole DNA Oligo", "100nmole DNA Oligo"),
                                 ("250nmole DNA Oligo", "250nmole DNA Oligo")])

    service = SelectField(label="Service",
                          choices=[("None", "None"), ("LabReady", "LabReady"),
                                   ("Analytical IE-HPLC pH 12.0", "Analytical IE-HPLC pH 12.0"),
                                   ("Analytical RP-HPLC", "Analytical RP-HPLC"),
                                   ("Conductivity Measurement", "Conductivity Measurement"),
                                   ("Fluorometric Scan (ABS/EM)", "Fluorometric Scan (ABS/EM)"),
                                   ("Na+Salt Exchange", "Na+Salt Exchange")])

    pair_id = HiddenField()

    submit = SubmitField("Add Primer & Send For Checking")


class Receive(Form):
    primer = SelectField('Primer')

    dt_received = DateField('Date Received',
                            format='%Y-%m-%d')

    lot_no = TextField("Lot Number")

    submit = SubmitField("Mark Primer as Recieved")


class Search(Form):
    term = TextField("Search")
    submit = SubmitField("Search")

class BulkPrimer(Form):
    data = TextAreaField("Paste Primers")
    submit = SubmitField("Process Primers")

