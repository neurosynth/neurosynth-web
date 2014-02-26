from nsweb.core import db
db=db()

##unable to create image file. I *think* its one to many for feature to images placeholder code. DO NOT RUN plz and thnk u

class Peak(db.Model):
    __tablename__ = 'peak'
    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(db.Integer,db.ForeignKey('study.pmid'))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
      
      name        :string, :index => true
      label        :string, :index => true
    kind    :string, :index => true
    comments    :text
    stat        :string
      image_file    :string
      json_file      :string
      timestamps
    display :boolean, :default => true
    download :boolean, :default => true
