from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
import nsweb.settings

app=None
db=None
manager=None

#Placeholder for possible need for restful
# from flask_restful import Api
# global api

def create_app(database_uri, debug=True):
    global app, db, manager
    app = Flask(__name__)
#    app.debug = debug
    app.config['DEBUG'] = debug
    app.config['DEBUG_WITH_APTANA'] = nsweb.settings.DEBUG_WITH_APTANA

    # set up your database
#    app.engine = create_engine(database_uri)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    db = SQLAlchemy(app)
    # add your modules
#     app.register_module(frontend)
    
    # other setup tasks

    manager = APIManager(app,flask_sqlalchemy_db=db)
    import studies.studies
    import features.features
#     api = Api(app)

    return (app, db, manager)
