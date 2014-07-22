import datetime
from nsweb.core import db
from nsweb.models.users import User
from nsweb.models.images import Image

class Download(db.Model):
    ''' Track all image downloads. '''
    id = db.Column(db.Integer, primary_key = True)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    ip = db.Column(db.String(15))
    created_at =  db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    user = db.relationship(User, backref=db.backref('downloads',cascade='all, delete-orphan'))
    