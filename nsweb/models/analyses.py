import datetime
from nsweb.core import db
# from nsweb.models.users import User
# from nsweb.models.studies import Study
# from nsweb.models.images import AnalysisImage
from nsweb.models import *
from sqlalchemy.ext.hybrid import hybrid_property
import simplejson as json
from sqlalchemy.ext.associationproxy import association_proxy

class Analysis(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=True)
    uuid = db.Column(db.String(32), unique=True)
    ip = db.Column(db.String(15))
    created_at  =  db.Column(db.DateTime, default=datetime.datetime.utcnow)

    studies = association_proxy('inclusions', 'study')
    images = db.relationship('AnalysisImage', backref=db.backref('analysis', lazy='joined'), lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref=db.backref('analyses',cascade='all, delete-orphan'))

    @hybrid_property
    def studies(self):
        return json.loads(self._studies)

    @studies.setter
    def studies(self, value):
        self._studies = json.dumps(value)


class Inclusion(db.Model):
    """ Join table for Analysis <--> Study """
    analysis_id = db.Column(db.Integer, db.ForeignKey(Analysis.id), primary_key=True)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.pmid), primary_key=True)
    analysis = db.relationship(Analysis, backref=db.backref('inclusions',cascade='all, delete-orphan', lazy='dynamic'), lazy='joined')
    study = db.relationship(Study, backref=db.backref('inclusions',cascade='all, delete-orphan', lazy='dynamic'), lazy='joined')