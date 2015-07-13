from nsweb.core import db


class Frequency(db.Model):
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'),
                            primary_key=True)
    pmid = db.Column(db.Integer, db.ForeignKey('study.pmid'),
                     primary_key=True)
    frequency = db.Column(db.Float, default=1.)
    analysis = db.relationship(
        'Analysis',
        backref=db.backref('frequencies', cascade='all, delete-orphan'), lazy='joined')
    study = db.relationship(
        'Study',
        backref=db.backref('frequencies', cascade='all, delete-orphan'), lazy='joined')

    # def __init__(self, study, analysis, frequency):

    #     self.study = study
    #     self.analysis = analysis
    #     self.frequency = frequency
