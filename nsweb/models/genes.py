from nsweb.core import db


class Gene(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    symbol = db.Column(db.String(20), unique=True)
    locus_type = db.Column(db.String(40))
    synonyms = db.Column(db.String(200))
    images = db.relationship(
        'GeneImage', backref=db.backref('gene', lazy='joined'), lazy='dynamic')
