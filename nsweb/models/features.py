from nsweb.models import *

class Feature(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    feature=db.Column(db.String(100),unique=True)
    num_studies=db.Column(db.Integer)
    num_activations=db.Column(db.Integer)
    frequencies = association_proxy('frequencies','frequency')
    
    image_forward_inference=db.Column(db.String(1000),unique=True)
    image_reverse_inference=db.Column(db.String(1000),unique=True)
    image_display=db.Column(db.Boolean)
    image_download=db.Column(db.Boolean)
    image_name=db.Column(db.String(200))
    image_label=db.Column(db.String(200))
    image_kind=db.Column(db.String(200))
    image_comments=db.Column(db.String(200))

    
    def __init__(self, feature, num_studies=0, num_activations=0, image_forward_inference='', image_reverse_inference='', image_display=True,image_download=True):
        self.feature=feature
        self.num_studies=num_studies
        self.num_activations=num_activations
        self.image_forward_inference=image_forward_inference
        self.image_reverse_inference=image_reverse_inference
        self.image_display=image_display
        self.image_download=image_download

class Frequency(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), primary_key=True)
    pmid = db.Column(db.Integer, db.ForeignKey(Study.pmid), primary_key=True)
    frequency = db.Column(db.Float)
    feature = db.relationship(Feature, backref=db.backref('frequencies',cascade='all, delete-orphan'))
    study = db.relationship(Study, backref=db.backref('frequencies',cascade='all, delete-orphan'))
    
    def __init__(self, study, feature, frequency):
        self.study=study
        self.feature=feature
        self.frequency=frequency
