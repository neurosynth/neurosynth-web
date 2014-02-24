import cPickle
from nsweb.settings import SQLALCHEMY_DATABASE_URI, DATA_DIR, PICKLE_DATABASE, FEATURE_DATABASE, DEBUG
from nsweb.core import create_app
create_app(SQLALCHEMY_DATABASE_URI, debug=DEBUG)
from nsweb.core import db
from nsweb.models import studies, features


# Re-initialize database
def init_database(self):
    db.drop_all()
    db.create_all()

# Read in the study data (contains pickled data originally in the database.txt file)

def read_pickle_database(self):
    pickle_data = open( DATA_DIR + PICKLE_DATABASE,'rb')
    dataset = cPickle.load(pickle_data)
    pickle_data.close()
    return dataset

# Create Feature records--just the features themselves, not mapping onto Studies yet
def read_features_text(self):
    features_text=open(DATA_DIR + FEATURE_DATABASE)
    feature_list = features_text.readline().split()[1:]  # Feature names
    
    # Store mapping of studies --> features, where values are frequencies
    #features_text=map(str.split,features_text.readlines())
    feature_data = {}#map( lambda r: map(float,str.split(r)), features_text.readlines())
    for x in features_text:
        x=x.split()
        feature_data[int(x[0])] = map(float,x[1:])
    features_text.close()
    #feature_data=zip(*feature_data)
    return (feature_list,feature_data)

def add_features(self, feature_list):
        feature_dict={}
        for x in feature_list:
            feature_dict[x] = features.Feature(feature=x)
            db.session.add(feature_dict[x])
            db.session.commit()
        return feature_dict


def add_studies(self, dataset, (feature_list, feature_data), feature_dict):
    # Create Study records
    n_studies = len(dataset)
    for i,x in enumerate(dataset):
    #    print "STUDY: ", x.get('id'), "(%d/%d)" % (i+1, n_studies)
        study = studies.Study(
                              pmid=int(x.get('id')),
                              doi=x.get('doi'),
                              title=x.get('title'),
                              journal=x.get('journal'),
                              space=x.get('space'),
                              authors=x.get('authors'),
                              year=x.get('year'),
                              table_num=x.get('table_num'))
        db.session.add(study)
    
        # Create Peaks and attach to Studies
        peaks = [map(float, y) for y in x.get('peaks')]
        for coordinate in peaks:
            peak=studies.Peak(x=coordinate[0],y=coordinate[1],z=coordinate[2])
            study.peaks.append(peak)
            db.session.add(peak)
        
        # Map features onto studies via a Frequency join table that also stores frequency info
        pmid_frequencies=feature_data[study.pmid]
        for y in range(len(feature_list)):
            if pmid_frequencies[y] > 0.0:
                db.session.add(features.Frequency(study=study,feature=feature_dict[feature_list[y]],frequency=pmid_frequencies[y]))
                feature_dict[feature_list[y]].num_studies+=1
                feature_dict[feature_list[y]].num_activations+=len(peaks)
                  
        # Commit each study record separately. A bit slower, but conserves memory.
        db.session.commit()
