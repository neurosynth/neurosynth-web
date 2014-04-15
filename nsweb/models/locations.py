from nsweb.models import *
import nsweb

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    location_feature = association_proxy('location_feature', 'LocationFeature')
    images = db.relationship('LocationImage', backref=db.backref('location', lazy='joined'))

    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        
class LocationFeature(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey(Location.id), primary_key=True)
    value = db.Column(db.Float)
    feature = db.relationship(Feature, backref=db.backref('location_feature',cascade='all, delete-orphan'))
    location = db.relationship(Location, backref=db.backref('location_feature',cascade='all, delete-orphan'))
     
    def __init__(self, location, feature, value):
        self.location=location
        self.feature=feature
        self.value=value