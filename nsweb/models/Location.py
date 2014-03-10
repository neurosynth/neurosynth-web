from nsweb.models import *

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
#    feature_affects = 
    
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        
class FeatureAffects(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey(Location.id), primary_key=True)
    value = db.Column(db.Float)
    feature = db.relationship(Feature, backref=db.backref('frequencies',cascade='all, delete-orphan'))
    study = db.relationship(Study, backref=db.backref('frequencies',cascade='all, delete-orphan'))
    
    def __init__(self, study, feature, frequency):
        self.study=study
        self.feature=feature
        self.frequency=frequency
