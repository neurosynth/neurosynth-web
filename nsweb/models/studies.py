from nsweb.core import db

class Study(db.Model):
    __tablename__ = 'study'
    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    authors = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    year = db.Column(db.Integer)
    space = db.Column(db.String(10))
    peaks = db.relationship('Peak', backref=db.backref('study', lazy='joined'), lazy='dynamic')
    
    def __init__(self, pmid, doi, title, journal, authors, year, space):
        self.pmid=pmid
        self.doi=doi
        self.title=title
        self.authors=authors
        self.journal=journal
        self.year=year
        self.space=space

class Peak(db.Model):
    __tablename__ = 'peak'
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer,db.ForeignKey('study.pmid'))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z