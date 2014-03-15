from nsweb.models import *

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