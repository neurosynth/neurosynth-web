from nsweb.models import *

class Download(db.Model):
    ''' Track all image downloads. '''
    id = db.Column(db.Integer, primary_key = True)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id))
    ip = db.Column(db.String(15))
    