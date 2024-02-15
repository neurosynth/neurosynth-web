# Provides access to the application(app), database(db), and rest
# apimanager(apimanager). Also we're keeping functions that modify the
# core app globally and configuration here.

from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
# from flask_restless import APIManager
from flask_babelex import Babel
from flask_user import UserManager
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from flask_mail import Mail
from flask_cors import CORS
from nsweb.initializers import settings
from nsweb.initializers.assets import init_assets
from nsweb.initializers import make_celery
from importlib import import_module
from werkzeug.middleware.proxy_fix import ProxyFix

# Do this before anything else to ensure the MPL backend isn't implicitly
# set to something else, which could break everything if running in a container
import matplotlib
matplotlib.use('agg')


app = Flask('NSWeb', static_folder=settings.STATIC_FOLDER,
            template_folder=settings.TEMPLATE_FOLDER)
CORS(app)

# Set protocol and host correctly from X-Forwarded headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Caching
cache = Cache(config={'CACHE_TYPE': 'simple'})

# Initialize celery
celery = make_celery(app)
from nsweb import tasks

db = SQLAlchemy()
from nsweb.models.users import User

# API-related stuff
marshmallow = Marshmallow()

mail = Mail()


def setup_logging(logging_path, level):
    '''Setups logging in app'''
    from logging.handlers import RotatingFileHandler
    from logging import getLogger, getLevelName

    file_handler = RotatingFileHandler(logging_path)
    file_handler.setLevel(getLevelName(level))
    loggers = [app.logger, getLogger('sqlalchemy')]
    for logger in loggers:
        logger.addHandler(file_handler)


def create_app(debug=True, test=False):
    '''creates app instance, db instance, and apimanager instance'''

    app.config['DEBUG'] = debug

    # Generate DB URI
    if settings.SQL_ADAPTER == 'sqlite':
        db_uri = settings.SQLALCHEMY_SQLITE_URI
    elif settings.SQL_ADAPTER.startswith('post'):
        if test:
            db_to_use = settings.SQL_TEST_DB
        elif settings.DEBUG:
            db_to_use = settings.SQL_DEVELOPMENT_DB
        else:
            db_to_use = settings.SQL_PRODUCTION_DB
        # db_uri = 'postgres://postgres@%s:5432/%s' % (
        db_uri = 'postgres://%s:%s@%s:5432/%s' % (
            settings.SQL_USER,
            settings.SQL_PASSWORD,
            settings.SQL_HOST,
            db_to_use)
    else:
        raise ValueError("Value of SQL_ADAPTER in settings must be either"
                         "'sqlite' or 'postgres'")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "very_sekret"  # move this out of here eventually

    # Initialize assets
    init_assets(app)

    # Initialize caching
    db.init_app(app)
    cache.init_app(app)

    # i18n support
    Babel(app)

    # API
    marshmallow.init_app(app)

    # Set up mail stuff
    params = ['USER_EMAIL_SENDER_NAME', 'USER_EMAIL_SENDER_EMAIL']
    if settings.MAIL_ENABLE:
        params += ['MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SERVER',
                   'MAIL_PORT', 'MAIL_USE_SSL', 'MAIL_DEBUG']
        app.config['USER_ENABLE_FORGOT_PASSWORD'] = True
    app.config.update({(p, getattr(settings, p)) for p in params})
    mail.init_app(app)

    # Set up user management
    app.config['CSRF_ENABLED'] = True

    UserManager(app, db, User)

    # load blueprints
    register_blueprints()

    # set up logging
    setup_logging(logging_path=settings.LOGGING_PATH,
                  level=settings.LOGGING_LEVEL)

    @app.route('/robots.txt')
    def static_from_root():
         return send_from_directory(app.static_folder, request.path[1:])

def register_blueprints():
    blueprint_locations = [
        'nsweb.api',
        'nsweb.api.analyses',
        # 'nsweb.api.custom',
        'nsweb.api.images',
        'nsweb.api.locations',
        'nsweb.api.studies',
        'nsweb.api.decode',
        'nsweb.api.genes',
        'nsweb.controllers.home',
        'nsweb.controllers.analyses',
        # 'nsweb.controllers.custom',
        'nsweb.controllers.locations',
        'nsweb.controllers.studies',
        'nsweb.controllers.decode',
        'nsweb.controllers.genes'
    ]

    for loc in blueprint_locations:
        mod = import_module(loc)
        app.register_blueprint(getattr(mod, 'bp'))
