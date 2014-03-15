from nsweb.models import *

class Feature(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    feature=db.Column(db.String(100),unique=True)
    num_studies=db.Column(db.Integer)
    num_activations=db.Column(db.Integer)
    frequencies = association_proxy('frequencies','frequency')
#     images = association_proxy('images', 'FeatureImage')
    images = db.relationship('FeatureImage', primaryjoin=id==FeatureImage.foreign_id, uselist=True,foreign_keys=[id], backref=db.backref('feature', lazy='joined')) #lazy='dynamic')
    feature_affects = association_proxy('feature_affects', 'FeatureAffects')

    
    def __init__(self, feature, num_studies=0, num_activations=0, images=[], image_display=True,image_download=True):
        self.feature=feature
        self.num_studies=num_studies
        self.num_activations=num_activations
        self.images=images
        self.image_display=image_display
        self.image_download=image_download
