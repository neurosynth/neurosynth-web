from nsweb.core import db
from sqlalchemy.ext.associationproxy import association_proxy


class Study(db.Model):

    pmid = db.Column(db.Integer, primary_key=True, autoincrement=False)
    doi = db.Column(db.Text)
    title = db.Column(db.Text)
    authors = db.Column(db.Text)
    journal = db.Column(db.Text)
    year = db.Column(db.Integer)
    space = db.Column(db.Text)
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
