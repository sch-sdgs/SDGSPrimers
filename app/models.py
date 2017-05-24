from app.primers import db
from app.main import app

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False)
    admin = db.Column(db.Integer)

    def __init__(self, username, admin):
        self.username = username
        self.admin = admin

    def __repr__(self):
        return '<Users %r>' % (self.username)


class Freezers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    location = db.Column(db.String(20), unique=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user_rel = db.relationship("Users", lazy='joined', foreign_keys=[user])

    def __init__(self, name=None, location=None, user=None):
        self.name = name
        self.location = location
        self.user = user

    def __repr__(self):
        return '<Freezer %r>' % (self.name)


class Applications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    paired = db.Column(db.String(20), unique=False)

    def __init__(self, name=None, paired=None):
        self.name = name
        self.paired = paired

    def __repr__(self):
        return '<Application %r>' % (self.name)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

class Boxes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    rows = db.Column(db.Integer)
    columns = db.Column(db.Integer)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    freezer_id = db.Column(db.Integer, db.ForeignKey('freezers.id'), nullable=False)
    aliquots = db.Column(db.Integer)

    user_rel = db.relationship("Users", lazy='joined', foreign_keys=[user])
    freezer_rel = db.relationship("Freezers", lazy='joined', foreign_keys=[freezer_id])

    def __init__(self, name=None, rows=None, columns=None, user=None, freezer_id=None):
        self.name = name
        self.rows = rows
        self.columns = columns
        self.user = user
        self.freezer_id = freezer_id

    def __repr__(self):
        return '<Boxes %r>' % (self.name)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result


class Primers(db.Model):
    __tablename__ = 'primers'
    __searchable__ = ['alias','id']

    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(20), unique=False)
    sequence = db.Column(db.String(100), unique=True)
    orientation = db.Column(db.Integer, unique=False)
    pair_id = db.Column(db.Integer, unique=False)
    mod_5 = db.Column(db.String(20), unique=False)
    mod_3 = db.Column(db.String(20), unique=False)
    scale = db.Column(db.String(20), unique=False)
    purification = db.Column(db.String(20), unique=False)
    service = db.Column(db.String(20), unique=False)
    date_designed = db.Column(db.String(20), unique=False)
    user_designed = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_checked = db.Column(db.String(20), unique=False)
    user_checked = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_ordered = db.Column(db.String(20), unique=False)
    user_ordered = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lot_no = db.Column(db.String(30), unique=False)
    date_received = db.Column(db.String(20), unique=False)
    user_received = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # box_id = db.ForeignKey('boxes.id')
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'), nullable=False)
    row = db.Column(db.Integer, unique=False)
    column = db.Column(db.Integer, unique=False)
    date_reconstituted = db.Column(db.String(20), unique=False)
    concentration = db.Column(db.Integer, unique=False)
    user_reconstituted = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_acceptance = db.Column(db.String(20), unique=False)
    worklist = db.Column(db.Integer, unique=False)
    user_acceptance = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # status = db.ForeignKey('status.id')
    status = db.Column(db.Integer, unique=False)
    current = db.Column(db.Integer, unique=False)
    application = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    historial_alias = db.Column(db.String(20), unique=False)

    box_rel = db.relationship("Boxes", lazy='joined', foreign_keys=[box_id])
    user_designed_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_designed])
    user_checked_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_checked])
    user_ordered_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_ordered])
    user_received_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_received])
    user_reconstituted_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_reconstituted])
    user_acceptance_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_acceptance])
    application_rel = db.relationship("Applications", lazy='joined', foreign_keys=[application])

    def __init__(self, alias=None, sequence=None, orientation=None, scale=None, date=None, date_designed=None, user_designed=None,
                 purification=None, service=None, mod_5=None, mod_3=None, current=None, pair_id=None, status=None, box_id=None, application=None, historial_alias=None, user_checked=None, date_checked=None):
        self.alias = alias
        self.sequence = sequence
        self.orientation = orientation
        self.mod_5 = mod_5
        self.mod_3 = mod_3
        self.scale = scale
        self.date = date
        self.purification = purification
        self.service = service
        self.user_designed = user_designed
        self.current = current
        self.date_designed = date_designed
        self.application = application
        self.historial_alias = historial_alias
        self.user_checked = user_checked
        self.date_checked = date_checked

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

    def __repr__(self):
        return '<alias %r>' % (self.alias)

class Aliquots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primer_id = db.Column(db.Integer, db.ForeignKey('primers.id'), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.id'), nullable=False)
    row = db.Column(db.Integer)
    column = db.Column(db.Integer)
    date_aliquoted = db.Column(db.String(20), unique=False)
    user_aliquoted = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    box_rel = db.relationship("Boxes", lazy='joined', foreign_keys=[box_id])
    primer_rel = db.relationship("Primers", lazy='joined', foreign_keys=[primer_id])
    user_aliquoted_rel = db.relationship("Users", lazy='joined', foreign_keys=[user_aliquoted])

    def __init__(self, primer_id=None, box_id=None, row=None, column=None, date_aliquoted=None, user_aliquoted=None):
        self.primer_id = primer_id
        self.box_id = box_id
        self.row = row
        self.column = column
        self.date_aliquoted = date_aliquoted
        self.user_aliquoted = user_aliquoted

    def __repr__(self):
        return '<Aliquots %r>' % (self.id)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

class Sets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    date = db.Column(db.String(20), unique=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current = db.Column(db.Integer, unique=False)

    user_rel = db.relationship("Users", lazy='joined', foreign_keys=[user])

    def __init__(self, name=None, date=None, user=None):
        self.name = name
        self.date = date
        self.user = user

    def __repr__(self):
        return '<Set %r>' % (self.name)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

class SetMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'), nullable=False)
    primer_id = db.Column(db.Integer, db.ForeignKey('primers.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    set_rel = db.relationship("Sets", lazy='joined', foreign_keys=[set_id])
    primer_rel = db.relationship("Primers", lazy='joined', foreign_keys=[primer_id])
    user_rel = db.relationship("Users", lazy='joined', foreign_keys=[user])


    def __init__(self, set_id=None, primer_id=None, user=None):
        self.set_id = set_id
        self.primer_id = primer_id
        self.user = user

    def __repr__(self):
        return '<SetMembers %r>' % (self.set_id)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

class SavedCarts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    date = db.Column(db.String(20), unique=False)
    ids = db.Column(db.PickleType, unique=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    user_rel = db.relationship("Users", lazy='joined', foreign_keys=[user])


    def __init__(self, name=None, date=None, ids=None, user=None):
        self.name = name
        self.date = date
        self.ids = ids
        self.user = user

    def __repr__(self):
        return '<Carts %r>' % (self.name)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

class Pairs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forward = db.Column(db.Integer, db.ForeignKey('primers.id'), nullable=False)
    reverse = db.Column(db.Integer, db.ForeignKey('primers.id'), nullable=False)


    forward_rel = db.relationship("Primers", lazy='joined', foreign_keys=[forward])
    reverse_rel = db.relationship("Primers", lazy='joined', foreign_keys=[reverse])


    def __init__(self, forward=None, reverse=None):
        self.forward = forward
        self.reverse = reverse

    def __repr__(self):
        return '<Pairs %r>' % (self.id)

    def to_dict(self):
        result = {}
        for attr, value in self.__dict__.iteritems():
            print attr
            if attr != '_sa_instance_state':
                result[attr] = value
        return result

if enable_search:
    whooshalchemy.whoosh_index(app, Primers)