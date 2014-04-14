from nsweb.models import *

class Study(db.Model):
    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    authors = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    year = db.Column(db.Integer)
    space = db.Column(db.String(10))
    table_num = db.Column(db.String(50))
    peaks = db.relationship('Peak', backref=db.backref('study', lazy='joined'), lazy='joined')
    features = association_proxy('frequencies','feature')

    def __init__(self, pmid, space, doi='', title='', journal='', authors='', year=0, table_num=''):
        self.pmid=pmid
        self.doi=doi
        self.title=title
        self.authors=authors
        self.journal=journal
        self.year=year
        self.space=space
        self.table_num=table_num
