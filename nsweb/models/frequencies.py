from nsweb.models import *

class Frequency(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), primary_key=True)
    pmid = db.Column(db.Integer, db.ForeignKey(Study.pmid), primary_key=True)
    frequency = db.Column(db.Float)
    feature = db.relationship(Feature, backref=db.backref('frequencies',cascade='all, delete-orphan', lazy='dynamic'), lazy='joined')
    study = db.relationship(Study, backref=db.backref('frequencies',cascade='all, delete-orphan', lazy='dynamic'), lazy='joined')
    def __init__(self, study, feature, frequency):
        self.study=study
        self.feature=feature
        self.frequency=frequency