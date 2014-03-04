from nsweb.models import *

class Feature(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    feature=db.Column(db.String(100),unique=True)
    num_studies=db.Column(db.Integer)
    num_activations=db.Column(db.Integer)
    frequencies = association_proxy('frequencies','frequency')
    images = db.relationship('Image', backref=db.backref('feature', lazy='joined'), lazy='dynamic')
    
    image_forward_inference=db.Column(db.String(1000),unique=True)
    image_reverse_inference=db.Column(db.String(1000),unique=True)
    image_display=db.Column(db.Boolean)
    image_download=db.Column(db.Boolean)
    image_name=db.Column(db.String(200))
    image_label=db.Column(db.String(200))
    image_kind=db.Column(db.String(200))
    image_comments=db.Column(db.String(200))

    
    def __init__(self, feature, num_studies=0, num_activations=0):
        self.feature=feature
        self.num_studies=num_studies
        self.num_activations=num_activations

class Frequency(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'), primary_key=True)
    pmid = db.Column(db.Integer, db.ForeignKey('study.pmid'), primary_key=True)
    frequency = db.Column(db.Float)
    feature = db.relationship(Feature, backref=db.backref('frequencies',cascade='all, delete-orphan'))
    study = db.relationship('Study')
    
    def __init__(self, study, feature, frequency):
        self.study=study
        self.feature=feature
        self.frequency=frequency
