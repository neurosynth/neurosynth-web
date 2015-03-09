# Provides access to the application(app), database(db), and rest
# apimanager(apimanager). Also we're keeping functions that modify the
# core app globally and configuration here.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_restless import APIManager
from flask.ext.babel import Babel
from flask.ext.user import UserManager, SQLAlchemyAdapter
from slimish_jinja import SlimishExtension
from flask.ext.cache import Cache
from flask.ext.marshmallow import Marshmallow
from nsweb.initializers import settings
from nsweb.initializers.assets import init_assets
from nsweb.initializers import make_celery


app = Flask('NSWeb', static_folder=settings.STATIC_FOLDER,
            template_folder=settings.TEMPLATE_FOLDER)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
# manager = Manager(app)

# Caching
cache = Cache(config={'CACHE_TYPE': 'simple'})

# Initialize celery
celery = make_celery(app)

db = SQLAlchemy()
_blueprints = []

# API-related stuff
marshmallow = Marshmallow()


def setup_logging(logging_path, level):
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
        if settings.DEBUG:
            db_to_use = settings.MYSQL_DEVELOPMENT_DB
        else:
            db_to_use = settings.MYSQL_PRODUCTION_DB
        db_uri = 'mysql://%s:%s@localhost/%s' % (
            settings.MYSQL_USER, settings.MYSQL_PASSWORD, db_to_use)
    else:
        raise ValueError("Value of SQL_ADAPTER in settings must be either"
                         "'sqlite' or 'mysql'")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.secret_key = "very_sekret"  # move this out of here eventually

    # Add slim support
    Flask.jinja_options['extensions'].append(SlimishExtension)

    # Initialize assets
    init_assets(app)

    # Initialize caching
    db.init_app(app)
    cache.init_app(app)

    # i18n support
    Babel(app)

    # API
    marshmallow.init_app(app)

    # Set up user management
    app.config['CSRF_ENABLED'] = True
    app.config['USER_ENABLE_EMAIL'] = False
    from nsweb.models.users import User
    db_adapter = SQLAlchemyAdapter(db, User)
    UserManager(db_adapter, app)

    # load blueprints
    register_blueprints()


def add_blueprint(blueprint):
    _blueprints.append(blueprint)


def register_blueprints():
    # creates and registers blueprints in nsweb.blueprints
    import nsweb.controllers.home
    import nsweb.controllers.studies
    import nsweb.controllers.analyses
    import nsweb.controllers.locations
    # import nsweb.controllers.api
    import nsweb.api
    import nsweb.controllers.images
    import nsweb.controllers.decode
    import nsweb.controllers.genes
    # import nsweb.controllers.analyze
    # import nsweb.controllers.topics

    for blueprint in _blueprints:
        app.register_blueprint(blueprint)
