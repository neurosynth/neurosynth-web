from nsweb.core import db
db=db()

##unable to create image file. I *think* its one to many for feature to images placeholder code. DO NOT RUN plz and thnk u

class Images(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.Integer,db.ForeignKey('feature.id'))
    name=db.Column(db.String(200))
    label=db.Column(db.String(200))
    kind=db.Column(db.String(200))
    comments=db.Column(db.String(200))
    stat=db.Column(db.String(200))
    image_file=db.Column(db.String(200))
    display=db.Column(db.Boolean)
    download=db.Column(db.Boolean)
   
    def __init__(self,name,label,kind,comments='',stat='',image_file,display=True,download=True):
        self.name=name
        self.label=label
        self.kind=kind
        self.comments=comments
        self.stat=stat
        self.image_file=image_file
        self.display=display
        self.download=download