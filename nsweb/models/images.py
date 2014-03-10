from nsweb.models import *

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
    
    foreign=db.Column('type', db.String(50))
    foreign_id=db.Column(db.Integer)
#     db.ForeignKeyConstraint(['foreign','foreign_id'])
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
    __mapper_args__={'polymorphic_identity':'Feature'}
    db.ForeignKeyConstraint(['foreign_id'],['Feature.id]'])

class LocationImage(Image):
    __mapper_args__={'polymorphic_identity':'Location'}
    db.ForeignKeyConstraint(['foreign_id'],['Location.id]'])
## is constraint needed since we already have type? issue is what will the query pull back?
