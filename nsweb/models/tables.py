from nsweb.models import *

class Table(db.Model):

    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    authors = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    study = db.relationship('Study', backref=db.backref('tables'))
    peaks = db.relationship('Peak', backref=db.backref('table', lazy='joined'), lazy='dynamic')
    analyses = association_proxy('frequencies', 'analyses')