# Provides access to the application(app), database(db), and rest apimanager(apimanager). Also we're keeping functions that modify the core app globally and configuration here.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
from slimish_jinja import SlimishExtension

from nsweb.initializers.settings import STATIC_FOLDER, TEMPLATE_FOLDER
from nsweb.initializers.assets import init_assets


app=Flask('NSWeb', static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
db=SQLAlchemy()
_blueprints = []


def setup_logging(logging_path,level):
    '''Setups logging in app'''
    from logging.handlers import RotatingFileHandler
    from logging import getLogger, getLevelName
    
    file_handler = RotatingFileHandler(logging_path)
    file_handler.setLevel(getLevelName(level))
    loggers = [app.logger, getLogger('sqlalchemy')]
    for logger in loggers:
        logger.addHandler(file_handler)

def create_app( database_uri, debug=True, aptana=True):
    '''creates app instance, db instance, and apimanager instance'''
    app.config['DEBUG'] = debug
    app.config['DEBUG_WITH_APTANA'] = aptana
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.test_request_context().push() #have to create a request context for flask-salalchemy
    db.init_app(app)
    Flask.jinja_options['extensions'].append(SlimishExtension)
#     Flask.jinja_options['']
#     autoescape = True
    init_assets(app)
#     apimanager.init_app(app, flask_sqlalchemy_db=db)

def add_blueprint(blueprint):
    _blueprints.append(blueprint)

def register_blueprints():

#     from nsweb.api import features
#     from nsweb.api import locations

    for blueprint in _blueprints:
        app.register_blueprint(blueprint)
        
