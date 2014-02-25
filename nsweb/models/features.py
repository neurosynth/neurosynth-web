from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from nsweb.models.studies import Studies

study=Studies.Study

class Features():
    global db
    db=SQLAlchemy()
    
    def __init__(self,db):
        self.db=db
        
    class Feature(db.Model):
        __tablename__ = 'feature'
        id=db.Column(db.Integer, primary_key=True)
        feature=db.Column(db.String(100),unique=True)
        num_studies=db.Column(db.Integer)
        num_activations=db.Column(db.Integer)
        frequencies = association_proxy('frequencies','frequency')
        
        def __init__(self, feature, num_studies=0, num_activations=0):
            self.feature=feature
            self.num_studies=num_studies
            self.num_activations=num_activations
    
    class Frequency(db.Model):
        __tablename__ = 'frequency'
        feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'), primary_key=True)
        pmid = db.Column(db.Integer, db.ForeignKey('study.pmid'), primary_key=True)
        frequency = db.Column(db.Float)
        feature = relationship(Features.Feature, backref=backref('frequencies',cascade='all, delete-orphan'))
        study = relationship('study')
        
        def __init__(self, study, feature, frequency):
            self.study=study
            self.feature=feature
            self.frequency=frequency
    