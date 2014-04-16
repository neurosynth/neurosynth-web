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
        '''
        Returns an optimized query using euclidean distance to find closest peaks within a radius of x, y, z
        '''
        # find peaks in a box then run heavier euclidean distance formula on what's left
        return Peak.query.filter(cls.x<=x+radius,cls.x>=x-radius,cls.y<=y+radius,cls.y>=y-radius,cls.z<=z+radius,cls.z>=z-radius,(x-cls.x)*(x-cls.x)+(y-cls.y)*(y-cls.y)+(z-cls.z)*(z-cls.z) <= radius*radius)
