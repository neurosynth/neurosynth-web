from nsweb.models import *
import nsweb

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    location_analysis = association_proxy('location_analysis', 'LocationAnalysis')
    images = db.relationship('LocationImage', backref=db.backref('location', lazy='joined'))

    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        
# class LocationAnalysis(db.Model):
#     analysis_id = db.Column(db.Integer, db.ForeignKey(Analysis.id), primary_key=True)
#     location_id = db.Column(db.Integer, db.ForeignKey(Location.id), primary_key=True)
#     value = db.Column(db.Float)
#     analysis = db.relationship(Analysis, backref=db.backref('location_analysis',cascade='all, delete-orphan'))
#     location = db.relationship(Location, backref=db.backref('location_analysis',cascade='all, delete-orphan'))
     
#     def __init__(self, location, analysis, value):
#         self.location=location
#         self.analysis=analysis
#         self.value=value