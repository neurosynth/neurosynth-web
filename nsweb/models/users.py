from nsweb.core import db
from flask.ext.user import UserMixin
import datetime

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key = True)
    active = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    # email = db.Column(db.String(120), unique = True)
    last_ip = db.Column(db.String(15))
    logins = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
#    role = db.Column(db.SmallInteger, default = ROLE_USER)
#    posts = db.relationship('comments', backref = 'images', lazy = 'dynamic')

    # def is_authenticated(self):
    #     return True

    # def is_active(self):
    #     return True

    # def is_anonymous(self):
    #     return False

    # def get_id(self):
    #     return unicode(self.id)

    # def __repr__(self):
    #     return '<User %r>' % (self.nickname)