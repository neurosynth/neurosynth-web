from nsweb.core import db
from sqlalchemy.ext.associationproxy import association_proxy
import datetime
from nsweb.models.users import User
from nsweb.models.frequencies import Frequency


class AnalysisSet(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    n_analyses = db.Column(db.Integer, default=0)
    type = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.now)


class Analysis(db.Model):

    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    analysis_set_id = db.Column(db.Integer, db.ForeignKey(AnalysisSet.id))
    name = db.Column(db.String(100) ,unique=False)
    n_studies = db.Column(db.Integer, default=0)
    n_activations = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    studies = association_proxy('frequencies', 'study')
    # images = db.relationship('AnalysisImage', backref=db.backref('analysis', lazy='joined'), lazy='dynamic')
    analysis_set = db.relationship('AnalysisSet', backref=db.backref(
        'analyses', cascade='all'))
    display = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.now)

    __mapper_args__ = {
        'polymorphic_identity': 'analysis',
        'polymorphic_on': type
    }

class TermAnalysis(Analysis):
    __tablename__ = 'term_analysis'
    id = db.Column(db.Integer, db.ForeignKey('analysis.id'), primary_key=True)
    images = db.relationship('TermAnalysisImage', backref=db.backref('analysis',
                             cascade='all'))
    cog_atlas = db.Column(db.Text, nullable=True)  # Cognitive Atlas RDF data
    __mapper_args__ = {
        'polymorphic_identity': 'term'
    }

    @property
    def reverse_inference_image(self):
        """ Convenience method for accessing the reverse inference image. """
        return self.images[1]


class TopicAnalysis(Analysis):

    __tablename__ = 'topic_analysis'
    id = db.Column(db.Integer, db.ForeignKey('analysis.id'), primary_key=True)
    terms = db.Column(db.Text)
    number = db.Column(db.Integer)
    images = db.relationship('TopicAnalysisImage', backref=db.backref('analysis',
                             cascade='all'))
    __mapper_args__ = {
        'polymorphic_identity': 'topic'
    }

    @property
    def reverse_inference_image(self):
        """ Convenience method for accessing the reverse inference image. """
        return self.images[1]


class CustomAnalysis(Analysis):

    __tablename__ = 'custom_analysis'
    id = db.Column(db.Integer, db.ForeignKey('analysis.id'), primary_key=True)
    uuid = db.Column(db.String(32), unique=True)
    ip = db.Column(db.String(15))
    images = db.relationship('CustomAnalysisImage', backref=db.backref('analysis',
                             cascade='all'))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref=db.backref('analyses',
                           cascade='all'))
    __mapper_args__ = {
        'polymorphic_identity': 'custom'
    }