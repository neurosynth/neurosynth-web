import datetime
from nsweb.core import db
from nsweb.models.users import User
from nsweb.models.analyses import AnalysisSet
from nsweb.models.images import Image
from sqlalchemy.ext.hybrid import hybrid_property
import simplejson as json


class DecodingSet(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    analysis_set_id = db.Column(db.Integer,
                                db.ForeignKey(AnalysisSet.id), nullable=True)
    analysis_set = db.relationship(AnalysisSet,
                                   backref=db.backref('decoding_set'))
    name = db.Column(db.String(20))
    n_images = db.Column(db.Integer)
    n_voxels = db.Column(db.Integer)
    is_subsampled = db.Column(db.Boolean)


class Decoding(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), unique=True, nullable=True)
    neurovault_id = db.Column(db.Integer, nullable=True)
    filename = db.Column(db.String(200))
    uuid = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(200))
    comments = db.Column(db.Text, nullable=True)
    display = db.Column(db.Boolean)
    download = db.Column(db.Boolean)
    _data = db.Column('data', db.Text, nullable=True)
    ip = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    image_decoded_at = db.Column(db.DateTime,
                                 onupdate=datetime.datetime.utcnow)
    image_modified_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    decoding_set_id = db.Column(db.Integer, db.ForeignKey(DecodingSet.id))
    decoding_set = db.relationship(
        DecodingSet, backref=db.backref('decodings',
                                        cascade='all, delete-orphan'))
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id), nullable=True)
    image = db.relationship(
        Image, backref=db.backref('decodings', cascade='all, delete-orphan'))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    user = db.relationship(
        User, backref=db.backref('uploads', cascade='all, delete-orphan'))

    @hybrid_property
    def data(self):
        return json.loads(self._data)

    @data.setter
    def data(self, value):
        self._data = json.dumps(value)
