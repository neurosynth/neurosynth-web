# Singleton provides access to the application(app), database(db), and rest apimanager(apimanager)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager

app=Flask('NSWeb')
db=SQLAlchemy()
apimanager=APIManager()

def setup_logging(logging_path,level):
    from logging.handlers import RotatingFileHandler
    from logging import getLogger, getLevelName
    
    file_handler = RotatingFileHandler(logging_path)
    file_handler.setLevel(getLevelName(level))
    loggers = [app.logger, getLogger('sqlalchemy')]
    for logger in loggers:
        logger.addHandler(file_handler)

def create_app( database_uri, debug=True, aptana=True):
    app.config['DEBUG'] = debug
    app.config['DEBUG_WITH_APTANA'] = aptana
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db.init_app(app)
    apimanager.init_app(app, flask_sqlalchemy_db=db)