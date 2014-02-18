import os
import cPickle
from nsweb.core import db
from nsweb.models import studies
#from nsweb.models import features

PWD = os.path.dirname(os.path.realpath(__file__))

pickleData = open( PWD + '/pickled.txt','rb')
dataset = cPickle.load(pickleData)
pickleData.close()

features_text=open(PWD + '/abstract_features.txt') 
feature_list = features_text.readline().split()
#features_text=map(str.split,features_text.readlines())
feature_data = {}#map( lambda r: map(float,str.split(r)), features_text.readlines())
for x in features_text:
    x=x.split()
    feature_data[int(x[0])]=map(float,x[1:])
features_text.close()
#feature_data=zip(*feature_data)

db.drop_all() #problem with this
db.create_all()

for x in dataset:
    study = studies.Study(
                          pmid=x.get('id'),
                          doi=x.get('doi'),
                          title=x.get('title'),
                          journal=x.get('journal'),
                          space=x.get('space'),
                          authors=x.get('authors'),
                          year=x.get('year'))
    peaks = [map(float, y) for y in x.get('peaks')]
    for coordinate in peaks:
        peak=studies.Peak(x=coordinate[0],y=coordinate[1],z=coordinate[2])
        study.peaks.append(peak)
        db.session.add(peak)
    
    db.session.add(study)
db.session.commit()

