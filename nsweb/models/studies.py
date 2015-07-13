from nsweb.core import db
from sqlalchemy.ext.associationproxy import association_proxy


class Study(db.Model):

    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    authors = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    year = db.Column(db.Integer)
    space = db.Column(db.String(10))
    peaks = db.relationship(
        'Peak', backref=db.backref('study', lazy='joined'), lazy='dynamic')
    analyses = association_proxy('frequencies', 'analysis')
    # analyses = association_proxy('inclusions', 'analysis')

    def serialize(self):
        return {'pmid': self.pmid, 'authors': self.authors,
                'journal': self.journal,
                'year': self.year,
                'title': '<a href="/studies/%s">%s</a>'
                % (self.pmid, self.title)}
