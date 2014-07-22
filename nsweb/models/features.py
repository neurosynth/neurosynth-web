from nsweb.models import *


class FeatureSet(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    num_features = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)


class Feature(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feature_set_id = db.Column(db.Integer, db.ForeignKey(FeatureSet.id))
    name = db.Column(db.String(100) ,unique=False)
    num_studies = db.Column(db.Integer, default=0)
    num_activations = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    # location_feature = association_proxy('feature_affects', 'FeatureAffects')
    studies = association_proxy('frequencies', 'study')
    images = db.relationship('FeatureImage', backref=db.backref('feature', lazy='joined'), lazy='dynamic')
    feature_set = db.relationship('FeatureSet', backref=db.backref('features', cascade='all, delete-orphan'))

    __mapper_args__ = {
        'polymorphic_identity':'feature',
        'polymorphic_on':type
    }


class Topic(Feature):

    id = db.Column(db.Integer, db.ForeignKey('feature.id'), primary_key = True)
    type = db.Column(db.String(50))
    terms = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity':'feature',
        'polymorphic_on':type
    }