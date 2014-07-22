
from nsweb.models.features import Feature
from nsweb.models.locations import Location
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak
from nsweb.models.frequencies import Frequency
from nsweb.models.images import FeatureImage, LocationImage, GeneImage
from nsweb.models.genes import Gene
from nsweb.initializers import settings
import os
from os.path import join, basename
from neurosynth.base.dataset import Dataset
from neurosynth.base import transformations
import nibabel as nb
import numpy as np
import pandas as pd
import random
from glob import glob
import simplejson as json
from copy import deepcopy



class DatabaseBuilder:


    def __init__(self, db, dataset=None, studies=None, features=None, reset_db=False, reset_dataset=False):
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
            reset_dataset: if True, will regenerate the pickled Neurosynth dataset.
        """

        # Load or create Neurosynth Dataset instance
        if dataset is None or reset_dataset or (isinstance(dataset, basestring) and not os.path.exists(dataset)):
            if (studies is None) or (features is None):
                raise ValueError("To generate a new Dataset instance, both studies and features must be provided.")
            dataset = Dataset(studies)
            dataset.add_features(features)
            dataset.save(settings.PICKLE_DATABASE, keep_mappables=True)
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


    def add_features_to_database(self, features, image_dir=None, min_studies=50, 
                                threshold=0.001, generate_images=True, update_db=True):
        """ Add new features to an existing Dataset and optionally update the 
        Features, Studies, etc. in the database. """

        old_features = set(self.dataset.feature_table.data.columns)

        self.dataset.add_features(features, min_studies=min_studies, 
                    threshold=threshold, merge='left')

        new_features = list(set(self.dataset.feature_table.data.columns) - old_features)
        print "Adding %d new features." % len(new_features)
        print new_features

        if update_db:
            self.add_features(new_features)
            self.add_studies(new_features)

        if generate_images:
            self.generate_feature_images(image_dir, new_features, update_db)

        self.dataset.save(settings.PICKLE_DATABASE, keep_mappables=True)


    def add_features(self, features=None, image_dir=None, reset=False):
        ''' Add Feature records to the DB. 
        Args:
            features: A list of feature names to add to the db. If None,  will use 
                all features in the Dataset.
            image_dir: folder to save generated feature images in. If None, do not 
                save any images.
        '''
        if reset:
            Feature.query.delete()

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
            FeatureImage(image_file=join(image_dir, name + '_pAgF_z_FDR_0.05.nii.gz'),
                label='%s: forward inference' % name,
                stat='z-score',
                display=1,
                download=1),
            FeatureImage(image_file=join(image_dir, name + '_pFgA_z_FDR_0.05.nii.gz'),
                label='%s: reverse inference' % name,
                stat='z-score',
                display=1,
                download=1)
        ])


    def add_studies(self, features=None, threshold=0.001, limit=None, reset=False):
        """ Add studies to the DB.
        Args:
            features: list of names of features to map studies onto. If None, use all available.
            threshold: Float or integer; minimum value in FeatureTable data array for inclusion.
            limit: integer; maximum number of studies to add (order will be randomized).
            reset: Drop all existing records before populating.
        Notes:
            By default, will not create new Study records if an existing one matches. This ensures 
            that we can gracefully add new feature associations without mucking up the DB.
            To explicitly replace old records, pass reset=True.
        """
        if reset:
            Study.query.delete()

        # For efficiency, get all feature data up front, so we only need to densify array once
        feature_data = self.dataset.get_feature_data(features=features)
        feature_names = feature_data.columns

        study_inds = range(len(self.dataset.mappables))
        if limit is not None:
            random.shuffle(study_inds)
            study_inds = study_inds[:limit]

        # Create Study records
        for i in study_inds:

            m = self.dataset.mappables[i]
            id = int(m.id)
            
            study = Study.query.get(id)
            if study is None:
                peaks = [Peak(x=float(p.x),
                              y=float(p.y),
                              z=float(p.z),
                              table=p.table_num
                              ) for (ind,p) in m.data.iterrows()]
                data = m.data.iloc[0]
                study = Study(
                          pmid=id,
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
                    self.features[feature_name][1] += 1
                    self.features[feature_name][2] += study.peaks.count()

         
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
            image_dir = join(settings.IMAGE_DIR, 'features')
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


    def generate_location_features(self, feature_dir=None, output_dir=None, 
            min_studies_at_voxel=50):
        """ Create json files containing feature data for every point in the brain. """
        if feature_dir is None:
            feature_dir = join(settings.IMAGE_DIR, 'features')
        if output_dir is None:
            output_dir = settings.LOCATION_FEATURE_DIR

        masker = self.dataset.masker

        study_names = self.dataset.image_table.ids
        feature_names = self.dataset.get_feature_names()
        imgs = np.array(self.dataset.image_table.data.todense())
        p_active = imgs.sum(1)
        # Save this for later
        ijk_reduced = np.array(np.where(p_active >= min_studies_at_voxel)[0]).squeeze()

        # Load rev inference z-score and posterior prob image data
        imgs = glob(join(feature_dir, '*pFgA_z.nii.gz'))
        print "Found %d imgs." % len(imgs)
        rev_inf_z = np.zeros((self.dataset.image_table.data.shape[0], len(imgs)))
        for i, img in enumerate(imgs):
            rev_inf_z[:,i] = masker.mask(img)

        imgs = glob(join(feature_dir, '*pFgA_given_pF=0.50.nii.gz'))
        rev_inf_pp = np.zeros((self.dataset.image_table.data.shape[0], len(imgs)))
        for i, img in enumerate(imgs):
            rev_inf_pp[:,i] = masker.mask(img)

        print "Done loading..."
        print len(ijk_reduced)
        print ijk_reduced.shape
        print ijk_reduced
        p_active = masker.unmask(p_active).squeeze()
        keep_vox = np.where(p_active >= min_studies_at_voxel)
        ijk = zip(*keep_vox)  # Exclude voxels with few studies
        xyz = transformations.mat_to_xyz(np.array(ijk))[:, ::-1]

        print "Processing voxels..."
        num_vox = len(xyz)
        num_features = len(feature_names)

        for i, seed in enumerate(xyz):

            location_name = '_'.join(str(x) for x in seed)
            featurefile = join(output_dir, '%s_features.txt' % location_name)
            # if os.path.isfile(featurefile): continue
            print "\nProcessing %d/%d..." % (i + 1, num_vox)
            ind = ijk_reduced[i]
            # print ind
            z_scores = list(rev_inf_z[ind,:].ravel())
            z_scores = ['%.2f' % x for x in z_scores]
            print "Getting posterior probs..."
            pp = list(rev_inf_pp[ind,:].ravel())
            pp = ['%.2f' % x for x in pp]
            # print pp.shape
            # print "Writing to file..."
            data = {
                'data': []
            }
            for j in range(num_features):
                # data['data'].append([feature_names[j], z_scores[j]])
                data['data'].append([feature_names[j], z_scores[j], pp[j]])
            json.dump(data, open(featurefile, 'w'))


    def generate_location_images(self, image_dir=None, add_to_db=False, min_studies=50, **kwargs):
        """ Create a full set of location-based coactivation images via Neurosynth. 
        Right now this isn't parallelized and will take a couple of days to run. 
        Args:
            min_studies: minimum number of active studies for a voxel to be processed
        """

        from neurosynth.base import transformations
        from neurosynth.analysis import meta

        if image_dir is None:
            image_dir = join(settings.IMAGE_DIR, 'coactivation')
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
                self.add_location_images(self, image_dir)


    def add_location_images(self, image_dir=None, search=None, limit=None, overwrite=False):
        """ Filter all the images in the passed directory and add records. """
        
        if image_dir is None:
            image_dir = join(settings.IMAGE_DIR, 'coactivation')

        if search is None:
            search = '*_pFgA_z.nii.gz'

        extra_assets = [
            {
                'name': 'YeoBucknerFCMRI',
                'path': join('/data/neurosynth/data/locations', 'fcmri', 'functional_connectivity_%d_%d_%d.nii.gz'),
                'label': 'Functional connectivity',
                'description': "This image displays resting-state functional connectivity for the seed region in a sample of 1,000 subjects. Image provided courtesy of Yeo, Buckner and colleagues. For details, see <a href='http://jn.physiology.org/content/106/3/1125.long'>Yeo et al (2011)</a>."
            }
        ]
        
        images = glob(join(image_dir, search))
        print "Found %d images to add." % len(images)

        if limit is None:
            limit = len(images)

        for img in images[:limit]:

            x, y, z = [int(i) for i in basename(img).split('_')[:3]]
            if (not overwrite) and self.db.session.query(Location).filter_by(x=x, y=y, z=z).count():
                continue
            location = Location(x=x, y=y, z=z)
            location.images = [LocationImage(
                image_file=img,
                label='coactivation: (%d, %d, %d)' % (x, y, z),
                stat='z-score',
                display=1,
                download=1)
            ]
            
            # Add any additional assets
            for xtra in extra_assets:
                xtra_path = xtra['path'] % (x, y, z)
                if os.path.exists(xtra_path):
                    location.images.append(LocationImage(
                        image_file = xtra_path,
                        label = xtra['label'],
                        display = 1,
                        download = 1
                        ))

            self.db.session.add(location)

        self.db.session.commit()

    def add_genes(self, gene_dir=None, reset=True):
        """ Add records for genes, working from a directory containing gene images. """
        if reset:
            Gene.query.delete()
        if gene_dir is None:
            gene_dir = settings.GENE_IMAGE_DIR
        genes = glob(join(gene_dir, "*.nii.gz"))
        print "Adding %d genes..." % len(genes)
        found = {}
        for (i, g) in enumerate(genes):
            symbol = basename(g).split('_')[2]
            if symbol == 'A' or symbol == 'CUST' or symbol.startswith('LOC') or symbol in found:
                continue
            found[symbol] = 1
            gene = Gene(name=symbol, symbol=symbol)
            gene.images = [GeneImage(
                image_file = g,
                label = "AHBA gene expression levels for " + symbol,
                stat = "z-score",
                display=1,
                download=0
                )]

            self.db.session.add(gene)
            if i % 1000 == 0:
                self.db.session.commit()

    def generate_decoding_data(self, features=None):
        """ Save image data for feature maps we use in decoding as a separate 
        numpy array for rapid use. """
        if features is None:
            features = dataset.get_feature_names()
        path = join(settings.IMAGE_DIR, 'features', '%s_pFgA_z.nii.gz')
        images = [path % f for f in features]
        images = [i for i in images if os.path.exists(i)]
        n_vox, n_studies = self.dataset.image_table.data.shape[0], len(features)
        data = np.zeros((n_vox, n_studies))
        for (i, img) in enumerate(images):
            data[:,i] = self.dataset.masker.mask(img)
        data = pd.DataFrame(data, columns=features)
        data.to_msgpack(settings.DECODING_DATA)

    def generate_topics(self, topic_keys, doc_topics):
        """ Seed the database with topics. """
        # images = glob(join(settings.TOPIC_DIR, 'images', '*_p?g?_z.nii.gz'))
        # temporarily store old FeatureTable while we analyze topics
        ft = deepcopy(self.dataset.feature_table)
        self.dataset.add_features(doc_topics)
        




