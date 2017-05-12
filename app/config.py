import os
basedir = os.path.dirname(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + basedir + '/resources/primers.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'resources')
WHOOSH_BASE = os.path.join(basedir + '/resources/')