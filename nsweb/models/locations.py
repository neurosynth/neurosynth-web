from nsweb.models import *

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    feature_affects = association_proxy('feature_affects', 'FeatureAffects')
   
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        
class FeatureAffects(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey(Location.id), primary_key=True)
    value = db.Column(db.Float)
    feature = db.relationship(Feature, backref=db.backref('feature_affects',cascade='all, delete-orphan'))
    location = db.relationship(Location, backref=db.backref('feature_affects',cascade='all, delete-orphan'))
     
    def __init__(self, location, feature, value):
        self.location=location
        self.feature=feature
        self.value=value
