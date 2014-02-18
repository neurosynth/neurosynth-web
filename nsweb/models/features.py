from nsweb.core import db
import studies
from sqlalchemy.ext.associationproxy import AssociationProxy

class Features(db.Model):
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id')),
    study_id = db.Column(db.Integer, db.ForeignKey('study.pmid')),
    frequency = db.Column(db.Float)
                    
class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_of_studies=db.Column(db.Integer)
    num_of_activations=db.Column(db.Integer)
    frequencies = AssociationProxy