# -*- coding: utf-8 -*-
from wtforms.fields.html5 import DateField
from app.queries import *
from flask_wtf import Form
from wtforms.fields import TextField, SubmitField, HiddenField, PasswordField, RadioField, BooleanField, SelectField, \
    TextAreaField
from wtforms.validators import Required, InputRequired
import datetime
import json
import os
import pprint
from cgi import escape
from wtforms.widgets import Select, HTMLString, html_params

__all__ = ('ExtendedSelectField', 'ExtendedSelectWidget')


class ExtendedSelectWidget(Select):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for item1, item2 in field.choices:
            if isinstance(item2, (list, tuple)):
                group_label = item1
                group_items = item2
                html.append('<optgroup %s>' % html_params(label=group_label))
                for inner_val, inner_label in group_items:
                    html.append(self.render_option(inner_val, inner_label, inner_val == field.data))
                html.append('</optgroup>')
            else:
                val = item1
                label = item2
                html.append(self.render_option(val, label, val == field.data))
        html.append('</select>')
        return HTMLString(''.join(html))


class ExtendedSelectField(SelectField):
    """
    Add support of ``optgroup`` grouping to default WTForms' ``SelectField`` class.
    Here is an example of how the data is laid out.
        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            )),
            ('other','None Of The Above')
        )
    It's a little strange that the tuples are (value, label) except for groups which are (Group Label, list of tuples)
    but this is actually how Django does it too https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    """
    widget = ExtendedSelectWidget()

    def pre_validate(self, form):
        """
        Don't forget to validate also values from embedded lists.
        """
        for item1, item2 in self.choices:
            if isinstance(item2, (list, tuple)):
                group_label = item1
                group_items = item2
                for val, label in group_items:
                    if val == self.data:
                        return
            else:
                val = item1
                label = item2
                if val == self.data:
                    return
        raise ValueError(self.gettext('Not a valid choice!'))


def convert_json_to_choices(json_file):
    with open(json_file) as json_data:
        all_data = json.load(json_data)

    result = []
    for i in all_data:
        choices = tuple()
        for choice in all_data[i]:
            choices = ((choice["value"], choice["label"]),) + choices
            group = (i, (choices))
        result.append(group)

    final = tuple(result)
    return final


class Primer(Form):
    alias = TextField("Primer Alias", validators=[Required()])
    sequence = TextField("Sequence", validators=[InputRequired()])
    chromosome = SelectField("Chromosome",
                             choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"),
                                      ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("12", "12"),
                                      ("13", "13"), ("14", "14"), ("15", "15"), ("16", "16"), ("17", "17"),
                                      ("18", "18"), ("19", "19"), ("20", "20"), ("21", "21"), ("22", "22"), ("X", "X"),
                                      ("Y", "Y")])
    position = TextField("Position")

    application = SelectField('Application')

    m13 = BooleanField('Add M13 Tag?')

    orientation = RadioField('Orientation', choices=[(0, 'F'), (1, 'R')])

    dt = DateField('Date Designed',
                   format='%Y-%m-%d', default=datetime.date.today)
    purification = SelectField(label='Purification',
                               choices=[("DESALT", "Desalt"), ("RP1", "Cartridge"),
                                        ("HPLC", "HPLC"), ("PAGE", "PAGE")])

    mod_5_choices = convert_json_to_choices(os.path.dirname(os.path.dirname(__file__)) + "/resources/5_prime_mods.json")

    mod_5 = ExtendedSelectField(label="5' Modification", choices=mod_5_choices)

    mod_3_choices = convert_json_to_choices(os.path.dirname(os.path.dirname(__file__)) + "/resources/3_prime_mods.json")

    mod_3 = ExtendedSelectField(label="3' Modification",
                                choices=mod_3_choices)

    scale = SelectField(label="Scale",
                        choices=[("0.0250 UMO", "0.025 " + u"μ" + "mole - This is unavailable for most modifications"),
                                 ("0.0500 UMO", "0.05 " + u"μ" + "mole"),
                                 ("1.0000 UMO", "1 " + u"μ" + "mole"),
                                 ("10.0000 UMO", "10 " + u"μ" + "mole"),
                                 ("15.0000 UMO", "15 " + u"μ" + "mole")])

    # service = SelectField(label="Service",
    #                       choices=[("None", "None"), ("LabReady", "LabReady"),
    #                                ("Analytical IE-HPLC pH 12.0", "Analytical IE-HPLC pH 12.0"),
    #                                ("Analytical RP-HPLC", "Analytical RP-HPLC"),
    #                                ("Conductivity Measurement", "Conductivity Measurement"),
    #                                ("Fluorometric Scan (ABS/EM)", "Fluorometric Scan (ABS/EM)"),
    #                                ("Na+Salt Exchange", "Na+Salt Exchange")])

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
    application = SelectField("Application")
    submit = SubmitField("Process Primers")


class Comment(Form):
    comment = TextAreaField("Comment")
    object_id = HiddenField()
    submit = SubmitField("Add Comment")
