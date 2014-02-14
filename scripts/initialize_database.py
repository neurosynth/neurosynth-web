import nsweb.models.TOREMOVEmodels
import cPickle
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from nsweb.models import TOREMOVEmodels

SQLALCHEMY_DATABASE_URI = config.get('Database', 'SQLALCHEMY_DATABASE_URI')


pickleData = open(os.path.dirname(os.path.realpath(__file__)) + '../pickled.txt','rb')
dataset = cPickle.load(pickleData)
pickleData.close()

articles = {}
for x in dataset:
    TOREMOVEmodels.
    articles[x.get('id')] = ( {'title'   : x.get('title')},
                         {'authors' : x.get('authors')},
                         {'journal' : x.get('journal')},
                         {'year'    : x.get('year')},
                         {'peaks' : x.get('peaks')})

db.create_all()