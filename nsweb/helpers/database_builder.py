# Re-initialize database
def init_database(db):
    db.drop_all()
    db.create_all()

# Read in the study data (contains pickled data originally in the database.txt file)
def read_pickle_database(data_dir, pickle_database):
    import cPickle
    pickle_data = open( data_dir + pickle_database,'rb')
    dataset = cPickle.load(pickle_data)
    pickle_data.close()
    return dataset

# Reads features into memory. returns a list of features and a dictionary of those features with pmid as a key
def read_features_text(data_dir, feature_database):
    features_text=open(data_dir + feature_database)
    feature_list = features_text.readline().split()[1:] # List of feature names
    
    feature_data = {} # Store mapping of studies --> features, where key is pmid and values are frequencies
    for x in features_text:
        x=x.split()
        feature_data[int(x[0])] = map(float,x[1:])
    features_text.close()
    return (feature_list,feature_data)

def add_images(feature,image_dir):
    feature.image_forward_inference=image_dir+'_'+feature.feature+'_pAgF_z_FDR_0.05.nii.gz'
    feature.image_reverse_inference=image_dir+'_'+feature.feature+'_pFgA_z_FDR_0.05.nii.gz'
    feature.image_display=True
    feature.image_download=True
    
def add_features(db,feature_list, image_dir=''):
    '''Creates and commits features to db .feature list is a list of features to be created and committed. To add images specify a image directory. This returns a dictionary of the feature objects with the name as the key'''
    from nsweb.models.features import Feature

    feature_dict={}

    for name in feature_list:
        feature=Feature(feature=name)
        feature_dict[name] = feature
        if image_dir !='':
            add_images(feature,image_dir)
        db.session.add(feature_dict[name])
        db.session.commit()
    return feature_dict


def add_studies(db, dataset, feature_list, feature_data, feature_dict):
    from nsweb.models.studies import Study, Peak
    from nsweb.models.features import Frequency

    # Create Study records
    for i,x in enumerate(dataset):
        study = Study(
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
            peak=Peak(x=coordinate[0],y=coordinate[1],z=coordinate[2])
            study.peaks.append(peak)
#            db.session.add(peak)# TODO:is this needed???
        
        # Map features onto studies via a Frequency join table that also stores frequency info
        pmid_frequencies=feature_data[study.pmid]
        for y in range(len(feature_list)):
            if pmid_frequencies[y] > 0.0:
                db.session.add(Frequency(study=study,feature=feature_dict[feature_list[y]],frequency=pmid_frequencies[y]))
                feature_dict[feature_list[y]].num_studies+=1
                feature_dict[feature_list[y]].num_activations+=len(peaks)
                  
        # Commit each study record separately. A bit slower, but conserves memory.
        db.session.commit()