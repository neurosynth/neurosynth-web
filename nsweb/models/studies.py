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
    peaks = db.relationship('Peak', backref=db.backref('study', lazy='joined'), lazy='dynamic')
    frequencies = association_proxy('frequencies','frequency')

    
    def __init__(self, pmid, space, doi='', title='', journal='', authors='', year=0, table_num=''):
        self.pmid=pmid
        self.doi=doi
        self.title=title
        self.authors=authors
        self.journal=journal
        self.year=year
        self.space=space
        self.table_num=table_num
        
class Peak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(db.Integer,db.ForeignKey(Study.pmid))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

    def closest(self,edge_length,x,y,z):
        '''Finds closest peaks approximated to a cube. Because its SO Fast and Easy!'''
        return self.query.filter(x < x+edge_length and x>x-edge_length and y< y+edge_length and y>y-edge_length and z< z+edge_length and z>z-edge_length).all()
