import Studies

#TODO Reenable configs
#TODO reenable peaks

import os
import ConfigParser
import cPickle
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


#config = ConfigParser.ConfigParser()
#config.read(os.path.dirname(os.path.realpath(__file__)) + '../../config.cfg')
#SQLALCHEMY_DATABASE_URI = config.get('Database', 'SQLALCHEMY_DATABASE_URI')

app = Flask(__name__)
#if SQLALCHEMY_DATABASE_URI == '' :
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#else:
#    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

class Features():
    db.Table('features',
             
             )
    class Feature(db.Model):
        id = db.Column(db.Integer, primary_key=True)