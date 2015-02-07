from nsweb.core import db

class Gene(db.Model):

    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200), unique=True)
    symbol=db.Column(db.String(20), unique=True)
    images = db.relationship('GeneImage', backref=db.backref('gene', lazy='joined'), lazy='dynamic')
