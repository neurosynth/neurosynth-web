from nsweb.core import db
from flask.ext.user import UserMixin
import datetime


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    email = db.Column(db.String(120), unique=True)
    reset_password_token = db.Column(db.String(100), nullable=False,
                                     server_default='')
    confirmed_at = db.Column(db.DateTime())
    last_ip = db.Column(db.String(15))
    logins = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    active = db.Column('is_active', db.Boolean(), nullable=False,
                       server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')






