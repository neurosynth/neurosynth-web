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


class Study(db.Model):
    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    authors = db.Column(db.String(1000))
    year = db.Column(db.Integer)
#    peaks = deferred(db.Column(db.Blob,)) #try pickletype instead?
    peak_id = db.Column(db.Integer)
    space = db.Column(db.String(10))


    def peaksToPickle(self,peaks):
        return cPickle.dumps(peaks)
        
    def pickleToPeaks(self, pickle):
        return cPickle.load(pickle)
    
    def __init__(self, pmid, doi, title, journal, authors, year, peak_id, space):
        self.pmid=pmid
        self.doi=doi
        self.title=title
        self.journal=journal
        self.authors=authors
        self.year=year
#        self.peaks=peaksToPickle(peaks)
        self.peak_id=peak_id
        self.space=space

    def __repr__(self):
        return '<Study %r>' % self.title