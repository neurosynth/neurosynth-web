
from nsweb.models.analyses import TermAnalysis, TopicAnalysis, AnalysisSet
from nsweb.models.locations import Location
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak
from nsweb.models.frequencies import Frequency
from nsweb.models.decodings import DecodingSet
from nsweb.models.images import (Image, TermAnalysisImage, LocationImage,
                                 GeneImage, TopicAnalysisImage)
from nsweb.models.genes import Gene
from nsweb.initializers import settings
import os
from os.path import join, basename, exists
from os import makedirs
from neurosynth import Masker
from neurosynth.base.dataset import Dataset
from neurosynth.base import transformations
from neurosynth.analysis import meta
import nibabel as nb
import numpy as np
import pandas as pd
import random
from glob import glob
import json
from copy import deepcopy
import re



class DatabaseBuilder:


    def __init__(self, db, dataset=None, studies=None, features=None, reset_db=False, reset_dataset=False):
        """ Initialize instance from a pickled Neurosynth Dataset instance or a 
        pair of study and analysis .txt files. 
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
        if reset_db:
            print "WARNING: RESETTING DATABASE!!!"

        # Load or create Neurosynth Dataset instance
        if dataset is None or reset_dataset or (isinstance(dataset, basestring) and not os.path.exists(dataset)):
            print "\tInitializing a new Dataset..."
            if (studies is None) or (features is None):
                raise ValueError("To generate a new Dataset instance, both studies and analyses must be provided.")
            dataset = Dataset(studies)
            dataset.add_features(features)
            dataset.save(settings.PICKLE_DATABASE, keep_mappables=True)
        else:
            print "\tLoading existing Dataset..."
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


    def add_term_analyses(self, analyses=None, add_images=False, image_dir=None, reset=False):
        ''' Add Analysis records to the DB. 
        Args:
            analyses: A list of analysis names to add to the db. If None,  will use 
                all analyses in the Dataset.
            image_dir: folder to save generated analysis images in. If None, do not 
                save any images.
        '''
        if reset:
            for a in TermAnalysis.query.all():
                self.db.session.delete(a)
            for s in AnalysisSet.query.filter_by(type='terms').all():
                self.db.session.delete(s)

        if analyses is None:
            analyses = self._get_feature_names()
        else:
            analyses = list(set(self._get_feature_names()) & set(analyses))

        term_set = AnalysisSet(name='abstract terms', type='terms',
            description='Term-based meta-analyses. Studies are identified for '
            'inclusion based on the presence of terms in abstracts.')
        # Store analyses for faster counting of studies/activations
        self.analyses = {}

        for f in analyses:
            
            analysis = TermAnalysis(name=f)

            # elements are the Analysis instance, # of studies, and # of activations
            self.analyses[f] = [analysis, 0, 0]

            if add_images:
                self.add_analysis_images(analysis, image_dir)

            term_set.analyses.append(analysis)
            self.db.session.add(analysis)

        term_set.n_analyses = len(term_set.analyses)
        self.db.session.commit()


    def add_analysis_images(self, analysis, image_dir=None, reset=True):
        """ Create DB records for the reverse and forward meta-analysis images for the given analysis. 
        Args:
            analysis: Either a Analysis instance or the (string) name of a analysis to update. If a 
                string, first check self.analyses, and only retrieve from DB if not found. 
            image_dir: Location to find images in
            reset: If True, deletes any existing AnalysisImages before adding new ones
        """

        if isinstance(analysis, basestring):
            if hasattr(self, 'analyses') and analysis in self.analyses:
                analysis = self.analyses[analysis][0]
            else:
                analyses = Analysis.query.filter_by(name=name).all()
                if len(analyses) > 1:
                    raise ValueError("More than 1 analysis has the name %s! Please resolve the "
                        "conflict and try again." % name)
                elif not analyses:
                    return
                else:
                    analysis = analyses[0]

        analysis.images = []

        name = analysis.name

        if image_dir is None:
            image_dir = join(settings.IMAGE_DIR, 'analyses')

        # Image class depends on Analysis class
        if hasattr(analysis, 'terms'):
            image_class = TopicAnalysisImage
        else:
            image_class = TermAnalysisImage

        analysis.images.extend([
            image_class(image_file=join(image_dir, name + '_pAgF_z_FDR_0.01.nii.gz'),
                label='%s: forward inference' % name,
                stat='z-score',
                display=1,
                download=1),
            image_class(image_file=join(image_dir, name + '_pFgA_z_FDR_0.01.nii.gz'),
                label='%s: reverse inference' % name,
                stat='z-score',
                display=1,
                download=1)
        ])

        self.db.session.add(analysis)
        self.db.session.commit()


    def add_studies(self, analyses=None, threshold=0.001, limit=None, reset=False):
        """ Add studies to the DB.
        Args:
            analyses: list of names of analyses to map studies onto. If None, use all available.
            threshold: Float or integer; minimum value in AnalysisTable data array for inclusion.
            limit: integer; maximum number of studies to add (order will be randomized).
            reset: Drop all existing records before populating.
        Notes:
            By default, will not create new Study records if an existing one matches. This ensures 
            that we can gracefully add new analysis associations without mucking up the DB.
            To explicitly replace old records, pass reset=True.
        """
        if reset:
            Study.query.delete()

        # For efficiency, get all analysis data up front, so we only need to densify array once
        if analyses is None:
            analyses = self._get_feature_names()

        feature_data = self.dataset.get_feature_data(features=analyses)
        analysis_names = list(feature_data.columns)

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
                              table=str(p.table_num).replace('nan', '')
                              ) for (ind,p) in m.data.iterrows()]
                data = m.data.iloc[0]
                study = Study(
                          pmid=id,
                          space=data['space'],
                          doi=str(data['doi']).replace('nan', ''),
                          title=data['title'],
                          journal=data['journal'],
                          authors=data['authors'],
                          year=data['year'])
                study.peaks.extend(peaks)
                self.db.session.add(study)
             
            # Map analyses onto studies via a Frequency join table that also stores frequency info
            pmid_frequencies = list(feature_data.ix[m.id, :])

            for (y, analysis_name) in enumerate(analysis_names):
                freq = pmid_frequencies[y]
                if pmid_frequencies[y] >= threshold:
                    freq_inst = Frequency(study=study, analysis=self.analyses[analysis_name][0], frequency=freq)
                    self.db.session.add(freq_inst)

                    # Track number of studies and peaks so we can update Analysis table more
                    # efficiently later
                    self.analyses[analysis_name][1] += 1
                    self.analyses[analysis_name][2] += study.peaks.count()

         
        # Commit records in batches to conserve memory.
        # This is very slow because we're relying on the declarative base. Ideally should replace
        # this with use of SQLAlchemy core, but probably not worth the trouble considering we
        # only re-create the DB once in a blue moon.
            if (i+1) % 100 == 0:
                self.db.session.commit()

        self.db.session.commit()  # Commit any remaining studies

        # Update all analysis counts
        self._update_analysis_counts()


    def _map_analysis_to_studies(self, analysis):
        pass


    def _update_analysis_counts(self):
        """ Update the num_studies and num_activations fields for all analyses. """
        for k, f in self.analyses.items():
            f[0].n_studies = f[1]
            f[0].n_activations = f[2]
#            self.db.session.update(f) 
        self.db.session.commit()


    def generate_analysis_images(self, image_dir=None, analyses=None, add_to_db=True, 
                    overwrite=True, **kwargs):
        """ Create a full set of analysis meta-analysis images via Neurosynth. 
        Args:
            image_dir: Folder in which to store images. If None, uses default 
                location specified in SETTINGS.
            analyses: Optional list of analyses to limit meta-analysis to.
                If None, all available analyses are processed.
            add_to_db: if True, will create new AnalysisImage records, and associate 
                them with the corresponding Analysis record.
            overwrite: if True, always generate new meta-analysis images. If False, 
                will skip any analyses that already have images.
            kwargs: optional keyword arguments to pass onto the Neurosynth meta-analysis.
        """
        # Set up defaults
        if image_dir is None:
            image_dir = join(settings.IMAGE_DIR, 'analyses')
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

        if analyses is None:
            analyses = self._get_feature_names()

        # Remove analyses that already exist
        if not overwrite:
            files = glob(join(settings.IMAGE_DIR, 'analyses', '*_pFgA_z.nii.gz'))
            existing = [basename(f).split('_')[0] for f in files]
            analyses = list(set(analyses) - set(existing))

        # Meta-analyze all images
        meta.analyze_features(self.dataset, analyses, save=image_dir, q=0.01, **kwargs)

        # Create AnalysisImage records
        if add_to_db:
            for f in analyses:
                self.add_analysis_images(f, image_dir)

            self.db.session.commit()

    def generate_location_loadings(self, analysis_dir=None, output_dir=None,
                                   min_studies_at_voxel=50, voxel=True,
                                   coactivation=True):
        """ Create json files containing analysis data for every point in the brain. """

        if analysis_dir is None:
            analysis_dir = join(settings.IMAGE_DIR, 'analyses')
        if output_dir is None:
            output_dir = settings.LOCATION_FEATURE_DIR

        masker = self.dataset.masker

        study_names = self.dataset.image_table.ids
        p_active = self.dataset.image_table.data.sum(1)

        v = np.where(p_active >= min_studies_at_voxel)[0]
        # Save this for later
        ijk_reduced = np.array(v).squeeze()

        # Only use images contained in Analysis table--we don't want users being linked 
        # to analyses that don't exist in cases where there are orphaned images.
        analyses = self.db.session.query(Analysis.name).all()
        analyses = [i[0] for i in analyses]
        n_analyses = len(analyses)

        if coactivation:
            z = np.zeros((self.dataset.image_table.data.shape[0], n_analyses))


        if voxel:
            # Read in all rev inf z and posterior prob images
            rev_inf_z = np.zeros((self.dataset.image_table.data.shape[0], n_analyses))
            rev_inf_pp = np.zeros((self.dataset.image_table.data.shape[0], n_analyses))

            print "Reading in images..."
            for i, f in enumerate(analyses):

                if (i+1) % 100 == 0:
                    print "Loaded analysis #%d..." % (i+1)

                rev_inf_z[:,i] = masker.mask(join(analysis_dir, f + '_pFgA_z.nii.gz'))
                rev_inf_pp[:,i] = masker.mask(join(analysis_dir, f + '_pFgA_given_pF=0.50.nii.gz'))

            print "Done loading..."
            p_active = masker.unmask(p_active).squeeze()
            keep_vox = np.where(p_active >= min_studies_at_voxel)
            ijk = zip(*keep_vox)  # Exclude voxels with few studies
            xyz = transformations.mat_to_xyz(np.array(ijk))[:, ::-1]

            print "Processing voxels..."
            num_vox = len(xyz)

            for i, seed in enumerate(xyz):

                location_name = '_'.join(str(x) for x in seed)
                analysisfile = join(output_dir, '%s_analyses.txt' % location_name)
                # if os.path.isfile(analysisfile): continue
                if (i+1) % 1000 == 0:
                    print "\nProcessing %d/%d..." % (i + 1, num_vox)
                ind = ijk_reduced[i]
                z_scores = list(rev_inf_z[ind,:].ravel())
                z_scores = ['%.2f' % x for x in z_scores]
                pp = list(rev_inf_pp[ind,:].ravel())
                pp = ['%.2f' % x for x in pp]
                data = {
                    'data': []
                }
                for j in range(n_analyses):
                    data['data'].append([analyses[j], z_scores[j], pp[j]])
                json.dump(data, open(analysisfile, 'w'))


    def add_genes(self, gene_dir=None, reset=True):
        """ Add records for genes, working from a directory containing gene images. """

        if reset:
            for g in Gene.query.all():
                Gene.query.delete(g)

        if gene_dir is None:
            gene_dir = settings.GENE_IMAGE_DIR

        genes = glob(join(gene_dir, "*.nii.gz"))
        print "Adding %d genes..." % len(genes)
        found = {}
        for (i, g) in enumerate(genes):
            symbol = basename(g).split('_')[2]
            if symbol == 'A' or symbol == 'CUST' or symbol.startswith('LOC') or symbol in found or len(symbol) > 20:
                continue
            found[symbol] = 1
            gene = Gene.query.filter_by(symbol=symbol).first()
            if gene is None:
                gene = Gene(name=symbol, symbol=symbol)
            gene.images = [GeneImage(
                image_file=g,
                label="AHBA gene expression levels for " + symbol,
                stat="z-score",
                display=1,
                download=0
                )]

            self.db.session.add(gene)
            if i % 1000 == 0:
                self.db.session.commit()

    def add_topics(self, generate_images=True, add_images=True, top_n=20,
                   reset=False):
        """ Seed the database with topics.
        Args:
            generate_images (bool): if True, generates meta-analysis images for
                all topics.
            add_images (bool): if True, adds records for all images to the
                database.
            top_n: number of top-loading words to save.
            reset: if True, drops all existing TopicSets and TopicAnalysis
                records before repopulating.
        """
        for ts in AnalysisSet.query.filter_by(type='topics').all():
            self.db.session.delete(ts)
        for t in TopicAnalysis.query.all():
            self.db.session.delete(t)
 
        topic_sets = glob(join(settings.TOPIC_DIR, '*.json'))

        # Temporarily store the existing AnalysisTable so we don't overwrite it
        # feature_table = deepcopy(self.dataset.feature_table)

        topic_image_dir = join(settings.IMAGE_DIR, 'topics')

        for ts in topic_sets:
            data = json.load(open(ts))
            n = int(data['n_topics'])

            ts = AnalysisSet(name=data['name'], description=data['description'],
                          n_analyses=n, type='topics')
            self.db.session.add(ts)

            self.dataset.add_features(join(settings.TOPIC_DIR, 'analyses',
                                      data['name'] + '.txt'), append=False)
            key_data = open(join(settings.TOPIC_DIR, 'keys', data['name'] +
                           '.txt')).read().splitlines()

            topic_set_image_dir = join(topic_image_dir, data['name'])
            if not exists(topic_set_image_dir):
                os.makedirs(topic_set_image_dir)

            # Generate full set of topic images
            if generate_images:
                meta.analyze_features(
                    self.dataset, self.dataset.get_feature_names(),
                    output_dir=topic_set_image_dir, threshold=0.05, q=0.01)

            feature_data = self.dataset.feature_table.data

            # Get all valid Study ids for speed
            study_ids = [x[0] for x in set(self.db.session.query(Study.pmid).all())]

            for i in range(n):

                # Disable autoflush temporarily because it causes problems
                with self.db.session.no_autoflush:
                    terms = ', '.join(key_data.pop(0).split()[2:][:top_n])
                    topic = TopicAnalysis(name='v3-topic-%d' % i,
                                          terms=terms, number=i)

                    self.db.session.add(topic)
                    self.db.session.commit()

                    # Map onto studies
                    freqs = feature_data['topic%d' % i]
                    above_thresh = freqs[freqs >= 0.05]
                    srsly = 0
                    for s_id, f in above_thresh.iteritems():
                        s_id = int(s_id)
                        if s_id in study_ids:
                            srsly += 1
                            self.db.session.add(Frequency(
                                pmid=s_id, analysis=topic, frequency=f))

                    # Update counts
                    topic.n_studies = len(above_thresh)

                    self.db.session.commit()

                    if add_images:
                        self.add_analysis_images(topic, topic_set_image_dir)

                ts.analyses.append(topic)

            self.db.session.commit()

        # Restore original features
        # self.dataset.feature_table = feature_table

    def add_cognitive_atlas_nodes(self):
        """ Store data from the Cognitive Atlas for all available nodes. """
        RDF_PATH = join(settings.ASSET_DIR, 'misc')
        rdf_files = glob(join(RDF_PATH, '*.rdf'))
        if not rdf_files:
            raise IOError("No RDF files found in %s. Please make sure to "
                "place all .rdf dumps from the Cognitive Atlas in this "
                "directory." % RDF_PATH)

        nodes = {}
        for f in rdf_files:
            text = open(f).read()
            patt = 'rdf:about="(.*?)">.*?' \
                   '<skos:definition>(.*?)</skos.*?' \
                   '<skos:prefLabel>(.*?)</skos:prefLabel>'
            for m in re.findall(patt, text, re.S):
                url, definition, name = m
                nodes[name] = {
                    'definition': definition.strip(),
                    'url': url
                    }

        for ta in TermAnalysis.query.all():
            if ta.name in nodes:
                ta.cog_atlas = json.dumps(nodes[ta.name])
                self.db.session.add(ta)
        self.db.session.commit()

    def memory_map_images(self, include=['terms', 'topics', 'genes'],
                          reset=False):
        """ Create memory-mapped arrays containing all image data for one or
        more AnalysisSets.
        """

        mm_dir = settings.MEMMAP_DIR
        if not exists(mm_dir):
            os.makedirs(mm_dir)

        # Get mask
        masker = Masker(join(settings.IMAGE_DIR, 'anatomical.nii.gz'))
        mask_voxels = np.sum(masker.get_current_mask())

        def save_memmap(name, analysis_set, images, labels, voxels=None):

            # Delete old versions
            if reset:
                dec = DecodingSet.query.filter_by(name=name).all()
                for ds in dec:
                    self.db.session.delete(ds)

            # print term_labels
            open(join(mm_dir, '%s_labels.txt' % name), 'w') \
                .write('\n'.join(labels))

            sampled_vox = np.arange(mask_voxels)
            is_subsampled = (voxels is not None)
            if voxels is not None:
                # Either randomly select voxels, or use what was passed
                # TODO: sample uniformly from a 3D grid instead of randomly
                if isinstance(voxels, int):
                    sampled_vox = np.random.choice(sampled_vox, voxels,
                                                   replace=False)
                else:
                    sampled_vox = voxels
                np.save(join(mm_dir, '%s_voxels.npy' % name), sampled_vox)

            # Initialize memmap
            n_images = len(images)
            mm_file = join(mm_dir, '%s_images.dat' % name)
            mm = np.memmap(mm_file, dtype='float32', mode='w+',
                           shape=(len(sampled_vox), n_images))

            # Save key image stats--will need these to reconstruct raw values
            stats = np.zeros((n_images, 4))

            # Populate with standardized image data
            for i, img in enumerate(images):
                # Use unthresholded maps when possible
                img_file = re.sub('_FDR.*nii.gz', '.nii.gz', img)
                data = masker.mask(img_file)[sampled_vox]
                std, mean = data.std(), data.mean()
                mm[:, i] = (data - mean)/std
                stats[i, :] = [data.min(), data.max(), mean, std]

            stats = pd.DataFrame(stats, index=labels,
                                 columns=['min', 'max', 'mean', 'std'])
            stats.to_csv(join(mm_dir, '%s_stats.txt' % name), sep='\t')

            # Write metadata
            metadata = {
                'name': name,
                'n_voxels': len(sampled_vox),
                'n_images': n_images,
                'is_subsampled': is_subsampled
            }
            md_file = join(mm_dir, '%s_metadata.json' % name)
            open(md_file, 'w').write(json.dumps(metadata))

            # Flush
            del mm

            # Create DB record
            self.db.session.add(
                DecodingSet(name=name, n_images=n_images,
                            n_voxels=len(sampled_vox),
                            is_subsampled=is_subsampled,
                            analysis_set=analysis_set))
            self.db.session.commit()

        ### TERMS ###
        if 'terms' in include:

            print "\tCreating memmap of term image data..."

            analysis_set = AnalysisSet.query \
                .filter_by(type='terms').first()

            # Get all images and save labels
            images = [a.images[1].image_file for a in analysis_set.analyses]
            labels = [a.name for a in analysis_set.analyses]

            print "\t\tFound %d images." % len(images)

            # save both full and 20k voxel arrays
            save_memmap('terms_full', analysis_set, images, labels)
            save_memmap('terms_20k', analysis_set, images, labels, 20000)
            # also save posterior probability images
            images = [img.replace('_pFgA_z_FDR_0.01', '_pFgA_given_pF=0.50')
                      for img in images]
            save_memmap('terms_pp', analysis_set, images, labels)

        ### TOPICS ###
        if 'topics' in include:

            print "\tCreating memmap of topic image data..."

            analysis_set = AnalysisSet.query \
                .filter_by(name='v3-topics-200').first()

            # Get all images and save labels
            images = [a.images[1].image_file for a in analysis_set.analyses]
            labels = [a.name for a in analysis_set.analyses]

            print "\t\tFound %d images." % len(images)

            # save both full and 20k voxel arrays
            save_memmap('topics_full', analysis_set, images, labels)
            save_memmap('topics_20k', analysis_set, images, labels, 20000)
            # also save posterior probability images
            images = [img.replace('_pFgA_z_FDR_0.01', '_pFgA_given_pF=0.50') for
                      img in images]
            save_memmap('topics_pp', analysis_set, images, labels)

        ### GENES ###
        if 'genes' in include:

            print "\tCreating memmap of gene image data..."

            # Get all images and save labels
            genes = Gene.query.all()
            images = [g.images[0].image_file for g in genes]
            labels = [g.name for g in genes]

            # save only voxels where there were originally microarrays
            sample_img = join(settings.IMAGE_DIR, 'sample_locations.nii.gz')
            voxels = masker.mask(sample_img)
            voxels = np.nonzero(voxels)[0]
            save_memmap('genes', None, images, labels, voxels)

    def _filter_analyses(self, analyses):
        """ Remove any invalid analysis names """
        # Remove analyses that start with a number
        analyses = [f for f in analyses if re.match('[a-zA-Z]+', f)]
        return analyses

    def _get_feature_names(self):
        """ Return all (filtered) analysis names in the Dataset instance """
        return self._filter_analyses(self.dataset.get_feature_names())
