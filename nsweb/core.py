from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
import nsweb.settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = nsweb.settings.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
manager = APIManager(app,flask_sqlalchemy_db=db)