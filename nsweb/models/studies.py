from nsweb.core import db

class Study(db.Model):
    pmid = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    journal = db.Column(db.String(200))
    space = db.Column(db.String(10))
    authors = db.Column(db.String(1000))
    year = db.Column(db.Integer)
    table_num = db.Column(db.Integer)
    peaks = db.relationship('Peak', backref=db.backref('study', lazy='joined'), lazy='dynamic')
    #features = 
    
#     def __init__(self, pmid, doi, title, journal, authors, year, peak_id, space):
#         self.pmid=pmid
#         self.doi=doi
#         self.title=title
#         self.journal=journal
#         self.space=space
#         self.authors=authors
#         self.year=year
#         self.table_num
#        self.peaks=peaksToPickle(peaks)

#     def __repr__(self):
#         return '<Study %r>' % self.title
    
class Peak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer,db.ForeignKey('study.pmid'))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    coordinate = db.Column(db.Float)