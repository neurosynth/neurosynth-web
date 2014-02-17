from nsweb.core import db
import studies

features = db.Table('features',
                    db.Column('feature_id', db.Integer, db.ForeignKey('feature.id')),
                    db.Column('study_id', db.Integer, db.ForeignKey('study.pmid')))
                    
class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer)
    study_id = db.Column(db.Integer)
    frequency = db.Column(db.Float)