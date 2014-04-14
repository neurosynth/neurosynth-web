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

    @classmethod
    def closestPeaks(cls, radius, x, y, z):
        '''Finds closest peaks approximated to a cube. Because its SO Fast and Easy!'''
        points = Peak.query.filter(cls.x<=x+radius).filter(cls.x>=x-radius).filter(Peak.y<=y+radius).filter(Peak.y>=y-radius).filter(Peak.z<=z+radius).filter(Peak.z>=z-radius)
        points = points.all()
        points = [p for p in points if pow(x-p.x, 2) + pow(y-p.y, 2) + pow(z-p.z, 2) <= radius] #euclidean distance filter
        return points