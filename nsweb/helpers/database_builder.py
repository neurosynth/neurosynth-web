# Re-initialize database
from nsweb.models.images import FeatureImage
from neurosynth.base import Dataset


class DatabaseBuilder:

    def __init__(self, db, dataset=None, studies=None, features=None):
        """ Initialize instance from either a pickled Neurosynth Dataset instance or a 
        pair of study and feature .txt files. Either dataset or (studies AND features)
        must be passed. Note that if a pickled Dataset is passed, it must contain 
        the list of Mappables (i.e., save() must have been called with keep_mappables 
        set to True). """

        # Load or create Neurosynth Dataset instance
        if dataset is None:
            if studies is None or features is None:
                raise ValueError("If dataset is None, both studies and features must be provided.")
                dataset = Dataset(studies)
                dataset.add_features(features)
        else:
            dataset = Dataset.load(dataset)

        self.dataset = dataset

        self.reset_database(db)


    def reset_database(self, db):
        db.drop_all()
        db.create_all()
        self.db = db


    def add_features(self, feature_list=None, image_dir=None):
        """ Add Feature records to the DB. If feature_list is None, use all features found 
        in the Dataset instance. Otherwise use only features named in the list. """
        if feature_list is None:
            feature_list = self.dataset.get_feature_names()

        self.features = {}
        for name in feature_list:
            feature = Feature(feature=name)
            self.features[name] = feature
            if image_dir is not None:
                self._add_feature_images(feature, image_dir)

            self.db.session.add(feature)
            self.db.session.commit()


    def _add_feature_images(self, feature, image_dir):
        """ Create DB records for the reverse and forward meta-analysis images for the given feature. """
        feature.images.extend([
                              FeatureImage(image_file=image_dir+'_'+feature.feature+'_pAgF_z_FDR_0.05.nii.gz', label='Forward Inference'),
                              FeatureImage(image_file=image_dir+'_'+feature.feature+'_pFgA_z_FDR_0.05.nii.gz', label='Reverse Inference')
                              ])


    def add_studies(self, feature_list=None, threshold=0):

        from nsweb.models.studies import Study, Peak
        from nsweb.models.features import Frequency

        # For efficiency, get all feature data up front, so we only need to densify array once
        feature_data = self.dataset.get_feature_data()
        feature_names = self.dataset.get_feature_names()  # Will be in same order as data

        # Create Study records
        for (i, m) in enumerate(self.dataset.mappables):

            data = m.data
            peaks = [Peak(x=float(coordinate[0]),
                          y=float(coordinate[1]),
                          z=float(coordinate[2])) for coordinate in m.get('peaks')]
            study = Study(
                                  pmid=int(m['id']),
                                  space=m['space'],
                                  doi=data['doi'],
                                  title=data['title'],
                                  journal=data['journal'],
                                  authors=data['authors'],
                                  year=data['year'],
                                  table_num=data['table_num'])
            study.peaks.extend(peaks)
            self.db.session.add(study)
             
            # Map features onto studies via a Frequency join table that also stores frequency info
            pmid_frequencies = list(feature_data[:,i])
            for (y, freq) in enumerate(pmid_frequencies):
                if pmid_frequencies[y] >= threshold:
                    self.db.session.add(Frequency(study=study,feature=feature_names[y],frequency=freq))

                      
            # Commit each study record separately. A bit slower, but conserves memory.
            self.db.session.commit()

        # Update all feature counts
        self._update_feature_counts()


    def _update_feature_counts(self):
        """ Update the num_studies and num_activations fields for all features. """
        # Rahul: Debug/finish this method. I figure it should be faster to loop over all
        # studies/features once than to repeatedly update Feature instances on the fly.
        # Perhaps SQLAlchemy has some SUM()-like method for summing fields of an
        # associated model?
        for f in self.features:
            f.num_studies = len(f.studies)
            for s in f.studies:
                f.num_activations += len(s.peaks)
        self.db.session.commit()


# # Read in the study data (contains pickled data originally in the database.txt file)
# def read_pickle_database(data_dir, pickle_database):
#     import cPickle
#     pickle_data = open( data_dir + pickle_database,'rb')
#     dataset = cPickle.load(pickle_data)
#     pickle_data.close()
#     return dataset

# # Reads features into memory. returns a list of features and a dictionary of those features with pmid as a key
# def read_features_text(data_dir, feature_database):
#     features_text=open(data_dir + feature_database)
#     feature_list = features_text.readline().split()[1:] # List of feature names
    
#     feature_data = {} # Store mapping of studies --> features, where key is pmid and values are frequencies
#     for x in features_text:
#         x=x.split()
#         feature_data[int(x[0])] = map(float,x[1:])
#     features_text.close()
#     return (feature_list,feature_data)

# def add_images(feature,image_dir):
#     feature.images.extend([
#                           FeatureImage(image_file=image_dir+'_'+feature.feature+'_pAgF_z_FDR_0.05.nii.gz', label='Forward Inference'),
#                           FeatureImage(image_file=image_dir+'_'+feature.feature+'_pFgA_z_FDR_0.05.nii.gz', label='Reverse Inference')
#                           ])
    
# def add_features(db,feature_list, image_dir=''):
#     '''Creates and commits features to db .feature list is a list of features to be created and committed. To add images specify a image directory. This returns a dictionary of the feature objects with the name as the key'''
#     from nsweb.models.features import Feature

#     feature_dict={}

#     for name in feature_list:
#         feature=Feature(feature=name)
#         feature_dict[name] = feature
#         if image_dir !='':
#             add_images(feature,image_dir)
#         db.session.add(feature)
#         db.session.commit()
#     return feature_dict



# def add_studies(db, dataset, feature_list, feature_data, feature_dict, threshold=0):
#     from nsweb.models.studies import Study, Peak
#     from nsweb.models.features import Frequency

#     # Create Study records
#     for _,data in enumerate(dataset):
#         peaks = [Peak(x=float(coordinate[0]),
#                       y=float(coordinate[1]),
#                       z=float(coordinate[2])) for coordinate in data.get('peaks')]
#         study = Study(
#                               pmid=int(data.get('id')),
#                               doi=data.get('doi'),
#                               title=data.get('title'),
#                               journal=data.get('journal'),
#                               space=data.get('space'),
#                               authors=data.get('authors'),
#                               year=data.get('year'),
#                               table_num=data.get('table_num'))
#         study.peaks.extend(peaks)
#         db.session.add(study)
    
#         # Create Peaks and attach to Studies
# #         peaks = [map(float, y) for y in x.get('peaks')]
# #         study.peaks = [Peak(x=coordinate[0],y=coordinate[1],z=coordinate[2]) for coordinate in [map(float, y) for y in x.get('peaks')]]
# #         for coordinate in peaks:
# #             peak=Peak(x=coordinate[0],y=coordinate[1],z=coordinate[2])
# #             study.peaks.append(peak)
         
#         # Map features onto studies via a Frequency join table that also stores frequency info
#         pmid_frequencies=feature_data[study.pmid]
#         for y in range(len(feature_list)):
#             if pmid_frequencies[y] >= threshold:
#                 db.session.add(Frequency(study=study,feature=feature_dict[feature_list[y]],frequency=pmid_frequencies[y]))
#                 feature_dict[feature_list[y]].num_studies+=1
#                 feature_dict[feature_list[y]].num_activations+=len(peaks)
                  
#         # Commit each study record separately. A bit slower, but conserves memory.
#         db.session.commit()