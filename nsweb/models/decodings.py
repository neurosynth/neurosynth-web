import datetime
from nsweb.core import db
from nsweb.models.users import User
from sqlalchemy.ext.hybrid import hybrid_property
import simplejson as json

# class JsonString(TypeDecorator):
#     impl = Text

#     def process_result_value(self, value, dialect):
#         if value is None:
#             return None
#         else:
#             return json.loads(value)

#     def process_bind_param(self, value, dialect):
#         if value is None:
#             return None
#         else:
#             return json.dumps(value)

class Decoding(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(255), unique=True)
    neurovault_id = db.Column(db.Integer, nullable=True)
    filename = db.Column(db.String(200))
    uuid = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(200))
    comments = db.Column(db.Text, nullable=True)
    display = db.Column(db.Boolean)
    download = db.Column(db.Boolean)
    _data = db.Column('data', db.Text, nullable=True)
    ip = db.Column(db.String(15))
    # type  =  db.Column(db.String(20))
    created_at  =  db.Column(db.DateTime, default=datetime.datetime.utcnow)
    image_decoded_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    image_modified_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    user = db.relationship(User, backref=db.backref('uploads',cascade='all, delete-orphan'))

    @hybrid_property
    def data(self):
        return json.loads(self._data)

    @data.setter
    def data(self, value):
        self._data = json.dumps(value)

