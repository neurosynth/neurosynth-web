
from nsweb.models.features import Feature
from nsweb.models.locations import Location
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak
from nsweb.models.frequencies import Frequency
from nsweb.models.images import FeatureImage, LocationImage
from nsweb.initializers import settings
import os
from neurosynth.base.dataset import Dataset
import numpy as np
import random



class DatabaseBuilder:


    def __init__(self, db, dataset=None, studies=None, features=None, reset_db=False):
        """ Initialize instance from a pickled Neurosynth Dataset instance or a 
        pair of study and feature .txt files. 
        Args:
            db: the SQLAlchemy database connection to use.
            dataset: an optional filename of a pickled neurosynth Dataset instance.
                Note that the Dataset must contain the list of Mappables (i.e., save() 
                    must have been called with keep_mappables set to True).
            studies: name of file containing activation data. If passed, a new Dataset 
                instance will be constructed.
            features: name of file containing feature data.
            reset_db: if True, will drop and re-create all database tables before 
                adding new content. If False (default), will add content incrementally.
        """

        # Load or create Neurosynth Dataset instance
        if dataset is None:
            if (studies is None) or (features is None):
                raise ValueError("If dataset is None, both studies and features must be provided.")
            dataset = Dataset(studies)
            dataset.add_features(features)
            dataset.save('/Users/tal/Downloads/dataset.pkl')
        else:
            dataset = Dataset.load(dataset)
            if features is not None:
                dataset.add_features(features)

        self.dataset = dataset
        self.db = db

        if reset_db:
            self.reset_database()


    def reset_database(self):
        ''' Drop and re-create all tables. '''
        self.db.drop_all()
        self.db.create_all()


    def add_features(self, features=None, image_dir=None):
        ''' Add Feature records to the DB. 
        Args:
            features: A list of feature names to add to the db. If None,  will use 
                all features in the Dataset.
            image_dir: folder to save generated feature images in. If None, do not 
                save any images.
        '''

        if features is None:
            features = self.dataset.get_feature_names()
        else:
            features = list(set(self.dataset.get_feature_names()) & set(features))

        # Store features for faster counting of studies/activations
        self.features = {}

        for f in features:
            
            feature = Feature(name=f)

            # elements are the Feature instance, # of studies, and # of activations
            self.features[f] = [feature, 0, 0]

            if image_dir is not None:
                self.add_feature_images(feature, image_dir)

            self.db.session.add(feature)

        self.db.session.commit()


    def add_feature_images(self, feature, image_dir, reset=True):
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
                feature = Feature.query.filter_by(name=name).first()
                if feature is None:
                    return

        if reset:
            feature.images = []

        name = feature.name

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


    def add_studies(self, features=None, threshold=0.001, limit=None):
        """ Add studies to the DB.
        Args:
            features: list of names of features to map studies onto. If None, use all available.
            threshold: Float or integer; minimum value in FeatureTable data array for inclusion.
            limit: integer; maximum number of studies to add (order will be randomized).
        """

        # For efficiency, get all feature data up front, so we only need to densify array once
        feature_data = self.dataset.get_feature_data(features=features).to_dense()
        feature_names = feature_data.columns

        study_inds = range(len(self.dataset.mappables))
        if limit is not None:
            random.shuffle(study_inds)
            study_inds = study_inds[:limit]

        # Create Study records
        for i in study_inds:

            m = self.dataset.mappables[i]
            peaks = [Peak(x=float(p.x),
                          y=float(p.y),
                          z=float(p.z),
                          table=p.table_num
                          ) for (ind,p) in m.data.iterrows()]
            data = m.data.iloc[0]
            study = Study(
                      pmid=int(m.id),
                      space=data['space'],
                      doi=data['doi'],
                      title=data['title'],
                      journal=data['journal'],
                      authors=data['authors'],
                      year=data['year'])
            study.peaks.extend(peaks)
            self.db.session.add(study)
             
            # Map features onto studies via a Frequency join table that also stores frequency info
            pmid_frequencies = list(feature_data.ix[m.id,:])

            for (y, feature_name) in enumerate(feature_names):
                freq = pmid_frequencies[y]
                if pmid_frequencies[y] >= threshold:
                    freq_inst = Frequency(study=study, feature=self.features[feature_name][0], frequency=freq)
                    self.db.session.add(freq_inst)

                    # Track number of studies and peaks so we can update Feature table more
                    # efficiently later
                    self.features[feature_name][1]+=1
                    self.features[feature_name][2]+=len(peaks)

         
        # Commit records in batches of 1000 to conserve memory.
        # This is very slow because we're relying on the declarative base. Ideally should replace 
        # this with use of SQLAlchemy core, but probably not worth the trouble considering we 
        # only re-create the DB once in a blue moon.
            if i % 1000 == 0:
                self.db.session.commit()

        self.db.session.commit()  # Commit any remaining studies

        # Update all feature counts
        self._update_feature_counts()


    def _update_feature_counts(self):
        """ Update the num_studies and num_activations fields for all features. """
        for k, f in self.features.items():
            f[0].num_studies = f[1]
            f[0].num_activations = f[2]
#            self.db.session.update(f) 
        self.db.session.commit()


    def generate_feature_images(self, image_dir=None, features=None, add_to_db=True, **kwargs):
        """ Create a full set of feature meta-analysis images via Neurosynth. 
        Args:
            image_dir: Folder in which to store images. If None, uses default 
                location specified in SETTINGS.
            features: Optional list of features to limit meta-analysis to.
                If None, all available features are processed.
            add_to_db: if True, will create new FeatureImage records, and associate 
                them with the corresponding Feature record.
            kwargs: optional keyword arguments to pass onto the Neurosynth meta-analysis.
        """
        from neurosynth.analysis import meta

        # Set up defaults
        if image_dir is None:
            image_dir = settings.IMAGE_DIR + 'features/'
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

        if features is None:
            features = self.dataset.get_feature_names()

        # Meta-analyze all images
        meta.analyze_features(self.dataset, features, save=image_dir, **kwargs)

        # Create FeatureImage records
        if add_to_db:
            for f in features:
                self.add_feature_images(f, image_dir)

            self.db.session.commit()


    def generate_location_images(self, image_dir=None, add_to_db=True, min_studies=50, **kwargs):
        """ Create a full set of location-based coactivation images via Neurosynth. 
        Right now this isn't parallelized and will take a couple of days to run. 
        Args:
            min_studies: minimum number of active studies for a voxel to be processed
        """

        from neurosynth.base import transformations
        from neurosynth.analysis import meta

        if image_dir is None:
            image_dir = settings.IMAGE_DIR + 'locations/'
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

        study_ids = self.dataset.image_table.ids

        # Identify all voxels we want to generate images for
        # imgs = np.array(self.dataset.image_table.data.todense())   # Make array dense
        imgs = self.dataset.image_table.data
        p_active = imgs.sum(1)   # Compute number of studies active at each voxel

        # Get array indices of all valid voxels--we'll need this later
        ijk_reduced = np.array(np.where(p_active >= min_studies)[0]).squeeze()

        # Project the voxel counts back into the original MNI space so we can look up coordinates
        p_active = self.dataset.masker.unmask(p_active).squeeze()

        # Keep only voxels with enough studies, and save coordinates as list of (i,j,k) tuples
        ijk = zip(*np.where(p_active >= min_studies))

        # Transform image-space coordinates into world-space coordinates
        xyz = transformations.mat_to_xyz(np.array(ijk))[:,::-1]

        num_vox = len(xyz)

        # Loop over valid voxels and generate coactivation images
        for i, seed in enumerate(xyz):

            voxel_index = ijk[i]
            num_active = p_active[voxel_index]

            # Get the right row by looking up index in the array we vectorized earlier
            vi = ijk_reduced[i]
            row = imgs[vi,:]

            # Get the ids of the studies that activate at this voxel
            study_inds = np.where(row.toarray())[1]
            studies = [study_ids[s] for s in study_inds]

            # Filename based on (x,y,z) joined by underscore
            seed = seed.tolist()
            name = '_'.join(str(x) for x in seed)

            # Call Neurosynth to do the heavy lifting
            # network.coactivation(self.dataset, [seed], threshold=0.1, outroot=outroot)
            ma = meta.MetaAnalysis(self.dataset, studies, **kwargs)
            imgs_to_keep = ['pFgA_z_FDR_0.05']  # Just the reverse inference
            ma.save_results(output_dir=image_dir, prefix=name, image_list=imgs_to_keep)

            # Create a new Location record and add LocationImage
            if add_to_db:
                location = Location(x=seed[0], y=seed[1], z=seed[2])
                location.images = [LocationImage(
                    image_file=image_dir + '/' + name + '_' + imgs_to_keep[0] + '.nii.gz',
                    label='coactivation: (%d, %d, %d)' % tuple(seed),
                    stat='z-score',
                    display=1,
                    download=1)
                ]
                self.db.session.add(location)

        self.db.session.commit()
