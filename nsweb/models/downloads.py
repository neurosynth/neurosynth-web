from nsweb.models import *

class Download(db.Model):
    '''
    '''
    id = db.Column(db.Integer, primary_key = True)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
#   user_id =
    ip = db.Column(db.Integer)
    