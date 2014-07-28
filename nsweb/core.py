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

# Kind of a hack to deal with the fact that the db instance isn't aware of the app context, 
# so we end up with a global session that persists over time. This would be okay except that 
# MySQL's default isolation level is too high, so that new records created in one session
# can't be viewed in another until it closes. We should probably rewrite all 
# session interactions so they're scoped and close at the end of the request, but in the 
# meantime, we use apply_driver_hacks() to manually set the isolation level at engine creation.
# Solution borrowed from:
# http://stackoverflow.com/questions/12384323/when-a-flask-application-with-flask-sqlalchemy-is-running-how-do-i-use-mysql-cl
class UnlockedAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        if not "isolation_level" in options:
            options["isolation_level"] = "READ COMMITTED"  # For example
        return super(UnlockedAlchemy, self).apply_driver_hacks(app, info, options)


app=Flask('NSWeb', static_folder=settings.STATIC_FOLDER, template_folder=settings.TEMPLATE_FOLDER)
manager = Manager(app)

# Initialize celery
celery = make_celery(app)
from nsweb.tasks import *

db=UnlockedAlchemy()
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

    # Generate DB URI
    if settings.SQL_ADAPTER == 'sqlite':
        db_uri = settings.SQLALCHEMY_SQLITE_URI
    elif settings.SQL_ADAPTER == 'mysql':
        db_to_use = settings.MYSQL_DEVELOPMENT_DB if settings.DEBUG else settings.MYSQL_PRODUCTION_DB
        db_uri = 'mysql://%s:%s@localhost/%s' % (settings.MYSQL_USER, settings.MYSQL_PASSWORD, db_to_use)
    else:
        raise ValueError("Value of SQL_ADAPTER in settings must be either 'sqlite' or 'mysql'")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
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
        
