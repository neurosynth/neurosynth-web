from nsweb.models import *

class Feature(db.Model):

    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100),unique=True)
    num_studies=db.Column(db.Integer, default=0)
    num_activations=db.Column(db.Integer, default=0)
    studies = association_proxy('frequencies', 'study')
    location_feature = association_proxy('feature_affects', 'FeatureAffects')
    images = db.relationship('FeatureImage', backref=db.backref('feature', lazy='joined'), lazy='dynamic')
