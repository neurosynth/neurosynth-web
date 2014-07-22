from nsweb.core import db
from nsweb.models.features import Feature, Topic
from nsweb.models.locations import Location
from nsweb.models.genes import Gene
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

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'image'
    }

    def __init__(self,image_file, label=None, display=True, download=True, stat=None):#name,kind,comments,stat,
#         self.name=name
        self.label=label
#         self.kind=kind
#         self.comments=comments
        self.stat=stat
        self.image_file=image_file
        self.display=display
        self.download=download

class FeatureImage(Image):
    __mapper_args__={'polymorphic_identity': 'feature'}
    feature_id = db.Column(db.Integer, db.ForeignKey(Feature.id), nullable=True)

class LocationImage(Image):
    __mapper_args__={'polymorphic_identity': 'location'}
    location_id = db.Column(db.Integer, db.ForeignKey(Location.id), nullable=True)

class TopicImage(Image):
    __mapper_args__={'polymorphic_identity': 'topic'}
    topic_id = db.Column(db.Integer, db.ForeignKey(Topic.id), nullable=True)

class GeneImage(Image):
    __mapper_args__={'polymorphic_identity': 'gene'}
    gene_id = db.Column(db.Integer, db.ForeignKey(Gene.id), nullable=True)

