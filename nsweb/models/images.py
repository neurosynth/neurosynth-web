from nsweb.models.features import *
from nsweb.models.locations import *
from sqlalchemy.orm.relationships import foreign

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200))
    label=db.Column(db.String(200))
    kind=db.Column(db.String(200))
    comments=db.Column(db.String(200))
    stat=db.Column(db.String(200))
    image_file=db.Column(db.String(200))
    display=db.Column(db.Boolean)
    download=db.Column(db.Boolean)
    type = db.Column(db.String(20))
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey(Location.id), nullable=True)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'image'
    }
   
#     def __init__(self,image_file, label=None, display=True, download=True, stat=None):#name,kind,comments,stat,
# #         self.name=name
#         self.label=label
# #         self.kind=kind
# #         self.comments=comments
#         self.stat=stat
#         self.image_file=image_file
#         self.display=display
#         self.download=download
        
class FeatureImage(Image):
    __mapper_args__={'polymorphic_identity': 'feature'}
    feature = db.relationship(Feature, backref=db.backref('images',cascade='all, delete-orphan'))


class LocationImage(Image):
    __mapper_args__={'polymorphic_identity': 'location'}
    location = db.relationship(Location, backref=db.backref('images',cascade='all, delete-orphan'))