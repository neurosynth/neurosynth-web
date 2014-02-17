import cPickle
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from nsweb.models.TOREMOVEmodels import Study
from nsweb.models import TOREMOVEmodels

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Studies(db.Model):
    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    authors = db.Column(db.String(1000))
    year = db.Column(db.Integer)
#    peaks = deferred(db.Column(db.Blob,))
    peak_id = db.Column(db.Integer)
    space = db.Column(db.String(10))


    def peaksToPickle(self,peaks):
        return cPickle.dumps(peaks)
        
    def pickleToPeaks(self, pickle):
        return cPickle.load(pickle)


#SQLALCHEMY_DATABASE_URI = config.get('Database', 'SQLALCHEMY_DATABASE_URI')

PWD = os.path.dirname(os.path.realpath(__file__))

pickleData = open( PWD + '/pickled.txt','rb')
dataset = cPickle.load(pickleData)
pickleData.close()

featuresTxt = open(PWD + '/abstract_features.txt')
featuresList = featuresTxt.readline()
featuresTxt.close()

db.create_all()

for x in dataset:
    db.session.add(Studies(
                        pmid=x.get('id'),
                        doi=x.get('doi'),
                        title=x.get('title'),
                        journal=x.get('journal'),
                        authors=x.get('authors'),
                        year=x.get('year'),
                        peak_id=x.get('peak_id'),
                        space=x.get('space')))
    db.session.commit()