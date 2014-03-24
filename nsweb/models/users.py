from nsweb.models import *

class User(db.Model):
    '''
    '''
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique = True)
    ip = db.Column(db.Integer, unique = True)
#    role = db.Column(db.SmallInteger, default = ROLE_USER)
#    posts = db.relationship('comments', backref = 'images', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)