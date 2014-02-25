from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
import logging
from logging.handlers import RotatingFileHandler
from logging import getLogger

app=None
db=None
manager=None

#Placeholder for possible need for restful
# from flask_restful import Api
# global api
def setup_logging(self,logging_path,level):

    file_handler = RotatingFileHandler(logging_path)
    file_handler.setLevel(logging.getLevelName(level))
    loggers = [app.logger, getLogger('sqlalchemy')]
    for logger in loggers:
        logger.addHandler(file_handler)

def create_app( database_uri, debug=True, aptana=True):
    global app, db, manager
    app = Flask(__name__)
#    app.debug = debug
    app.config['DEBUG'] = debug
    app.config['DEBUG_WITH_APTANA'] = aptana

    # set up your database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db = SQLAlchemy(app)
    # add your modules
#     app.register_module(frontend)
    
    # other setup tasks

    manager = APIManager(app,flask_sqlalchemy_db=db)
#     api = Api(app)

    return (app, db, manager)
