from nsweb.models import *

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
    
    @classmethod
    def closestPeaks(radius,x,y,z):
        '''Finds closest peaks approximated to a cube. Because its SO Fast and Easy!'''
        points = Peak.query.filter(x <= x+radius and x>=x-radius and y<= y+radius and y>=y-radius and z<= z+radius and z>=z-radius).all() #fast cube db search
        points = [p for p in points if pow(x-p.x, 2) + pow(y-p.y, 2) + pow(z-p.z, 2) <= radius] #euclidean distance filter
        return points
        
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