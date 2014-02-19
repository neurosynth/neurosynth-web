import os
import cPickle
from nsweb.core import db
from nsweb.models import studies, features

#from nsweb.models import features

PWD = os.path.dirname(os.path.realpath(__file__))

db.drop_all()
db.create_all()

pickleData = open( PWD + '/pickled.txt','rb')
dataset = cPickle.load(pickleData)
pickleData.close()

features_text=open(PWD + '/abstract_features.txt')
feature_dict={}
feature_list = features_text.readline().split()[1:]
for x in feature_list:
    feature_dict[x] = features.Feature(feature=x)
    db.session.add(feature_dict[x])
db.session.commit()

#features_text=map(str.split,features_text.readlines())
feature_data = {}#map( lambda r: map(float,str.split(r)), features_text.readlines())
for x in features_text:
    x=x.split()
    feature_data[int(x[0])] = map(float,x[1:])
features_text.close()
#feature_data=zip(*feature_data)

for x in dataset:
    study = studies.Study(
                          pmid=int(x.get('id')),
                          doi=x.get('doi'),
                          title=x.get('title'),
                          journal=x.get('journal'),
                          space=x.get('space'),
                          authors=x.get('authors'),
                          year=x.get('year'),
                          num_table=int(x.get('table_num')))
    peaks = [map(float, y) for y in x.get('peaks')]
    db.session.add(study)

    for coordinate in peaks:
        peak=studies.Peak(x=coordinate[0],y=coordinate[1],z=coordinate[2])
        study.peaks.append(peak)
        db.session.add(peak)
    
    pmid_frequencies=feature_data[study.pmid]
    for y in range(len(feature_list)):
        if pmid_frequencies[y] > 0.0:
            db.session.add(features.Frequency(study=study,feature=feature_dict[feature_list[y]],frequency=pmid_frequencies[y]))
            feature_dict[feature_list[y]].num_studies+=1
            feature_dict[feature_list[y]].num_activations+=len(peaks)
                
db.session.commit()

