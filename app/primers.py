from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import TimedRotatingFileHandler
import inspect
import itertools
from functools import wraps
from flask_login import current_user

#define app and db session

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'development key'
db = SQLAlchemy(app)
s = db.session

print app.config["SQLALCHEMY_DATABASE_URI"]
print app.config["WHOOSH_BASE"]

handler = TimedRotatingFileHandler('PerformanceSummary.log', when="d", interval=1, backupCount=30)
handler.setLevel(logging.INFO)

def message(f):
    """
    decorator that allows query methods to log their actions to a log file so that we can track users

    :param f:
    :return:
    """
    @wraps(f)
    def decorated_function(*args,**kwargs):
        method = f.__name__

        formatter = logging.Formatter('%(levelname)s|' + current_user.id + '|%(asctime)s|%(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

        args_name = inspect.getargspec(f)[0]
        args_dict = dict(itertools.izip(args_name, args))

        del args_dict['s']
        app.logger.info(method + "|" + str(args_dict))
        return f(*args, **kwargs)
    return decorated_function

#import modules and and register blueprints

from mod_admin.views import admin
from mod_primer.views import primer
from mod_box.views import box
from mod_freezer.views import freezer
from mod_set.views import set

app.register_blueprint(admin,url_prefix='/admin')
app.register_blueprint(primer,url_prefix='/primer')
app.register_blueprint(box,url_prefix='/box')
app.register_blueprint(freezer,url_prefix='/freezer')
app.register_blueprint(set,url_prefix='/set')




