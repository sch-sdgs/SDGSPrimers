import os
basedir = os.path.dirname(os.path.dirname(__file__))

database_path = basedir + '/resources/primers.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + database_path
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'resources')
WHOOSH_BASE = os.path.join(basedir + '/resources/')