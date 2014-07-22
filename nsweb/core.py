# Provides access to the application(app), database(db), and rest apimanager(apimanager). Also we're keeping functions that modify the core app globally and configuration here.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_restless import APIManager
from flask.ext.babel import Babel
from flask.ext.user import UserManager, SQLAlchemyAdapter
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from slimish_jinja import SlimishExtension

from nsweb.initializers import settings
from nsweb.initializers.assets import init_assets
from nsweb.initializers import make_celery


app=Flask('NSWeb', static_folder=settings.STATIC_FOLDER, template_folder=settings.TEMPLATE_FOLDER)
manager = Manager(app)

# Initialize celery
celery = make_celery(app)
from nsweb.tasks import *

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

def create_app(debug=True):
    '''creates app instance, db instance, and apimanager instance'''

    # Extra config stuff
    app.config['DEBUG'] = debug
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.secret_key = "very_sekret"  # move this out of here eventually
    app.test_request_context().push() #h ave to create a request context for flask-salalchemy
    db.init_app(app)

    # Add slim support
    Flask.jinja_options['extensions'].append(SlimishExtension)
    
    # Initialize assets
    init_assets(app)
    
    # Set up user management
    app.config['CSRF_ENABLED'] = True
    app.config['USER_ENABLE_EMAIL'] = False
    babel = Babel(app)
    from nsweb.models.users import User
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, app)

    #load blueprints
    register_blueprints()

def add_blueprint(blueprint):
    _blueprints.append(blueprint)

def register_blueprints():
    # creates and registers blueprints in nsweb.blueprints
    import nsweb.controllers.home
    import nsweb.controllers.studies
    import nsweb.controllers.features
    import nsweb.controllers.locations
    import nsweb.controllers.api
    import nsweb.controllers.images
    import nsweb.controllers.decode
    import nsweb.controllers.genes

    for blueprint in _blueprints:
        app.register_blueprint(blueprint)
        
