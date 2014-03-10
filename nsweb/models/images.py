from nsweb.models import *
from flask_restless.helpers import primary_key_name

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
#    table = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200))
    label=db.Column(db.String(200))
    kind=db.Column(db.String(200))
    comments=db.Column(db.String(200))
    stat=db.Column(db.String(200))
    image_file=db.Column(db.String(200))
    display=db.Column(db.Boolean)
    download=db.Column(db.Boolean)
    
    foreign=db.Column('type', db.String(50), foreign_key=True)
    foreign_id=db.Column(db.Integer, foreign_key=True)
    db.ForeignKeyConstraint(['foreign','foreign_id'])
    __mapper_args__ = {'polymorphic_on': foreign}
   
    def __init__(self,name,label,kind,comments,stat,image_file,display=True,download=True):
        self.name=name
        self.label=label
        self.kind=kind
        self.comments=comments
        self.stat=stat
        self.image_file=image_file
        self.display=display
        self.download=download
        
class FeatureImage(Image):
    __mapper_args__={'polymorphic_identity':'FeatureImage'}
        

class LocationImage(Image):
    __mapper_args__={'polymorphic_identity':'LocationImage'}
        
