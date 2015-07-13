from nsweb.core import db
from sqlalchemy.ext.associationproxy import association_proxy


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    location_analysis = association_proxy('location_analysis',
                                          'LocationAnalysis')
    images = db.relationship(
        'LocationImage', backref=db.backref('location', lazy='joined'))

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
