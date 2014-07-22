import datetime
from nsweb.core import db
from nsweb.models.users import User

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    uuid = db.Column(db.String(32))
    label = db.Column(db.String(200))
    comments = db.Column(db.String(200))
    image_file = db.Column(db.String(200))
    display = db.Column(db.Boolean)
    download = db.Column(db.Boolean)
    ip = db.Column(db.String(15))
    type  =  db.Column(db.String(20))
    created_at  =  db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship(User, backref=db.backref('uploads',cascade='all, delete-orphan'))