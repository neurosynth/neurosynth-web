# Re-initialize database
from nsweb.models.features import Feature
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak
from nsweb.models.frequencies import Frequency
from nsweb.models.images import FeatureImage
from nsweb import settings
from neurosynth.base.dataset import Dataset

class DatabaseBuilder:

    def __init__(self, db, dataset=None, studies=None, features=None, reset_db=False):
        """ Initialize instance from either a pickled Neurosynth Dataset instance or a 
        pair of study and feature .txt files. Either dataset or (studies AND features)
        must be passed. Note that if a pickled Dataset is passed, it must contain 
        the list of Mappables (i.e., save() must have been called with keep_mappables 
        set to True). """

        # Load or create Neurosynth Dataset instance
        if dataset is None:
            if (studies is None) or (features is None):
                raise ValueError("If dataset is None, both studies and features must be provided.")
            dataset = Dataset(studies)
            dataset.add_features(features)
        else:
            dataset = Dataset.load(dataset)
            if features is not None:
                dataset.add_features(features)

        self.dataset = dataset
        self.db = db

        if reset_db:
            self.reset_database()

    def reset_database(self):
        self.db.drop_all()
        self.db.create_all()

    def add_features(self, feature_list=None, image_dir=None):
        """ Add Feature records to the DB. If feature_list is None, use all features found 
        in the Dataset instance. Otherwise use only features named in the list. """
        if feature_list is None:
            feature_list = self.dataset.get_feature_names()

        self.features = {}
        for name in feature_list:
            feature = Feature(feature=name)
            self.features[name] = [feature,0,0]#num_studies, num_activations)
            if image_dir is not None:
                self._add_feature_images(feature, image_dir)

            self.db.session.add(feature)
        self.db.session.commit()


    def _add_feature_images(self, feature, image_dir, reset=True):
        """ Create DB records for the reverse and forward meta-analysis images for the given feature. 
        Args:
            feature: Either a Feature instance or the (string) name of a feature to update. If a 
                string, first check self.features, and only retrieve from DB if not found. 
            image_dir: Location to find images in
            reset: If True, deletes any existing FeatureImages before adding new ones
        """
        if isinstance(feature, basestring):
            if hasattr(self, 'features') and feature in self.features:
                feature = self.features[feature][0]
            else:
                feature = Feature.query.filter_by(feature=feature).first()

        if reset:
            feature.images = []

        name = feature.feature

        feature.images.extend([
            FeatureImage(image_file=image_dir+'_'+name+'_pAgF_z_FDR_0.05.nii.gz',
                label='%s: forward inference' % name,
                stat='z-score',
                display=1,
                download=1),
            FeatureImage(image_file=image_dir+name+'_pFgA_z_FDR_0.05.nii.gz',
                label='%s: reverse inference' % name,
                stat='z-score',
                display=1,
                download=1)
        ])

    def add_studies(self, feature_list=None, threshold=0.001):
        """ Add studies to the DB.
        Args:
            threshold: Float or integer; minimum value in FeatureTable data array for inclusion.
        """

        # For efficiency, get all feature data up front, so we only need to densify array once
        feature_data = self.dataset.get_feature_data()
        feature_names = self.dataset.get_feature_names()  # Will be in same order as data

        # Create Study records
        for (i, m) in enumerate(self.dataset.mappables):

            data = m.data
            peaks = [Peak(x=float(coordinate[0]),
                          y=float(coordinate[1]),
                          z=float(coordinate[2])) for coordinate in m.peaks]
            study = Study(
                                  pmid=int(m.id),
                                  space=m.space,
                                  doi=data['doi'],
                                  title=data['title'],
                                  journal=data['journal'],
                                  authors=data['authors'],
                                  year=data['year'],
                                  table_num=data['table_num'])
            study.peaks.extend(peaks)
            self.db.session.add(study)
             
            # Map features onto studies via a Frequency join table that also stores frequency info
            pmid_frequencies = list(feature_data[i,:])

            # Determine which features to check (or check all if feature_list is None)
            features_to_check = range(feature_data.shape[1])
            if feature_list is not None:
                features_to_check = [j for j in features_to_check if feature_names[j] in feature_list]

            for y in features_to_check:
                freq = pmid_frequencies[y]
                feature_name = feature_names[y]
                if pmid_frequencies[y] >= threshold:
                    freq_inst = Frequency(study=study, feature=self.features[feature_name][0], frequency=freq)
                    self.db.session.add(freq_inst)
                    self.features[feature_name][1]+=1
                    self.features[feature_name][2]+=len(peaks)

         
        # Commit records in batches of 1000 to conserve memory.
        # This is very slow because we're relying on the declarative base. Ideally should replace 
        # this with use of SQLAlchemy core, but probably not worth the trouble considering we 
        # only re-create the DB once in a blue moon.
            if i % 1000 == 0:
                self.db.session.commit()

        self.db.session.commit()  # Last < 1000 studies

        # Update all feature counts
        self._update_feature_counts()


    def _update_feature_counts(self):
        """ Update the num_studies and num_activations fields for all features. """
        # Rahul: Debug/finish this method. I figure it should be faster to loop over all
        # studies/features once than to repeatedly update Feature instances on the fly.
        # Perhaps SQLAlchemy has some SUM()-like method for summing fields of an
        # associated model?
        
        #TODO: I need a bit of help here. feature_data contains what I need with bincount or more likely count_nonzero. should go in neurosynth
        #This is my suggestion
        #removed numpy and whatnot. I had an idea. Do what we were doing before.
        #new idea. Keep features in memory. Commit later. just update num_studies ad num_activations as we go.
        for f in self.features.values():
            f[0].num_studies = f[1]
            f[0].num_activations = f[2]
#            self.db.session.update(f) # did this work before I added this?? Session should have been flushed... if it did work, I have no idea if the list was useless or what's going on with the features since they're tracked. This is prob best...yea.
        self.db.session.commit()

    def generate_feature_images(self, image_dir=None, feature_list=None, add_to_db=True, **kwargs):
        """ Create a full set of feature meta-analysis images via Neurosynth. 
        Args:
            image_dir: Folder in which to store images. If None, uses default 
                location specified in SETTINGS.
            feature_list: Optional list of features to limit meta-analysis to.
                If None, all available features are processed.
        """
        from neurosynth.analysis import meta

        # Set up defaults
        if image_dir is None:
            image_dir = settings.IMAGE_DIR

        if feature_list is None:
            feature_list = self.dataset.get_feature_names()

        # Meta-analyze all images
        meta.analyze_features(self.dataset, feature_list, save=image_dir + '/', **kwargs)

        # Create FeatureImage records
        if add_to_db:
            for f in feature_list:
                self._add_feature_images(f, image_dir)

            self.db.session.commit()


    def generate_location_images(self, image_dir=None, add_to_db=True, **kwargs):
        """ Create a full set of location-based coactivation images via Neurosynth. """



