from celery import Task
from nsweb.initializers import settings
from neurosynth import Masker
from neurosynth.base.dataset import Dataset
from neurosynth.analysis import meta
from celery.utils import cached_property
import numpy as np
import pandas as pd
import nibabel as nb
import matplotlib.pyplot as plt
import seaborn as sns
from nilearn.image import resample_img
from nsweb.core import celery
from os.path import join, basename, exists
from nsweb.tasks.scatterplot import scatter
import traceback
from glob import glob
import re
import json
from collections import OrderedDict


def load_image(masker, filename, save_resampled=True):
    """ Load an image, resampling into MNI space if needed. """
    filename = join(settings.DECODED_IMAGE_DIR, filename)
    img = nb.load(filename)
    if img.shape[:3] != (91, 109, 91):
        img = resample_img(
            img, target_affine=decode_image.anatomical.get_affine(),
            target_shape=(91, 109, 91), interpolation='nearest')
        if save_resampled:
            img.to_filename(filename)
    return masker.mask(img)

def xyz_to_mat(foci):
    """ Convert an N x 3 array of XYZ coordinates to matrix indices. """
    foci = np.hstack((foci, np.ones((foci.shape[0], 1))))
    mat = np.array([[-0.5, 0, 0, 45], [0, 0.5, 0, 63], [0, 0, 0.5, 36]]).T
    result = np.dot(foci, mat)  # multiply
    return np.round_(result).astype(int)  # need to round indices to ints


class Reference(object):

    def __init__(self, name, n_voxels, n_images, is_subsampled):

        self.name = name
        self.n_voxels = n_voxels
        self.n_images = n_images
        self.is_subsampled = is_subsampled

        # Link to memmap data
        mm_file = join(settings.MEMMAP_DIR, name + '_images.dat')
        self.data = np.memmap(mm_file, dtype='float32', mode='r',
                              shape=(n_voxels, n_images))
        # Link to labels
        lab_file = join(settings.MEMMAP_DIR, name + '_labels.txt')
        _labels = open(lab_file).read().splitlines()
        self.labels = OrderedDict(zip(_labels, range(len(_labels))))

        # Image stats
        stat_file = join(settings.MEMMAP_DIR, name + '_stats.txt')
        self.stats = pd.read_csv(stat_file, sep='\t')


class NeurosynthTask(Task):

    @cached_property
    def dataset(self):
        return Dataset.load(settings.PICKLE_DATABASE)

    @cached_property
    def masker(self):
        return Masker(join(settings.IMAGE_DIR, 'anatomical.nii.gz'))

    @cached_property
    def references(self):
        """ For efficiency, cache indices of all labels in all memmaps."""
        memmaps = {}
        for f in glob(join(settings.MEMMAP_DIR, '*_metadata.json')):
            md = json.load(open(f))
            memmaps[md['name']] = Reference(**md)
        return memmaps

    @cached_property
    def anatomical(self):
        f = join(settings.IMAGE_DIR, 'anatomical.nii.gz')
        return nb.load(f)

    @cached_property
    def masks(self):
        """ Return a dict of predefined region masks. """
        maps = {
            'cortex': join(settings.MASK_DIR, 'cortex.nii.gz'),
            'subcortex': join(settings.MASK_DIR, 'subcortex_drewUpdated.nii.gz'),
            'hippocampus': join(settings.MASK_DIR, 'FSL_BHipp_thr0.nii.gz'),
            'accumbens': join(settings.MASK_DIR, 'FSL_BNAcc_thr0.nii.gz'),
            'amygdala': join(settings.MASK_DIR, 'FSL_BAmyg_thr0.nii.gz'),
            'putamen': join(settings.MASK_DIR, 'FSL_BPut_thr0.nii.gz'),
            'min4': join(settings.MASK_DIR, 'voxel_counts_r6.nii.gz')
        }
        for m, img in maps.items():
            maps[m] = load_image(self.masker, img)
        return maps

@celery.task(base=NeurosynthTask)
def save_uploaded_image(filename, **kwargs):
    pass

@celery.task(base=NeurosynthTask)
def decode_image(filename, reference, uuid, mask=None, drop_zeros=False,
                 **kwargs):
    """ Decode an image file.
    Args:
        filename (str): the local path to the image
        reference (dict): the name of the memmapped image set to compare with
        uuid (str): a unique identifier to use when writing the file
        mask (str): the name of an optional mask to use (e.g., 'subcortex')
        drop_zeros (bool): if True, only non-zero, non-NA voxels in the input
            map are used in the comparison.
    """
    mm_dir = settings.MEMMAP_DIR
    try:
        ref = decode_image.references[reference]

        # Load and standardize the target image
        data = load_image(decode_image.masker, filename)
        # Select voxels in sampling mask if it exists
        if ref.is_subsampled:
            index_file = join(mm_dir, ref.name + '_voxels.npy')
            if exists(index_file):
                voxels = np.load(index_file)
                data = data[voxels]

        # Drop voxels with zeros or NaN in input image
        voxels = np.arange(len(data))
        if drop_zeros:
            voxels = np.where((data != 0) & np.isfinite(data))[0]
            data = data[voxels]

        # standardize image and get correlation
        data = (data - data.mean())/data.std()
        r = np.dot(ref.data[voxels].T, data)/ref.n_voxels
        outfile = join(settings.DECODING_RESULTS_DIR, uuid + '.txt')
        labels = ref.labels.keys()
        pd.Series(r, index=labels).to_csv(outfile, sep='\t')
        return True
    except Exception, e:
        print traceback.format_exc()
        return False

@celery.task(base=NeurosynthTask)
def get_voxel_data(reference, x, y, z, get_pp=True):
    """ Return a voxel slice through the specified memory mapped numpy array.
    Typically used to identify the values at a given voxel for all images in a
    given DecodingSet--e.g., get z-score values of all term-based analyses.
    """
    try:
        x, y, z = int(x), int(y), int(z)
        ijk = xyz_to_mat(np.array([[x, y, z]]))
        space = np.zeros((91, 109, 91))
        space[tuple(ijk[0])] = 1
        ind = np.nonzero(get_voxel_data.masker.mask(space))[0]

        ref = get_voxel_data.references[reference + '_full']
        labels = ref.labels.keys()
        result = pd.Series(ref.data[ind, :].ravel(), index=labels, name='z')
        result = result * ref.stats['std'].values + ref.stats['mean'].values

        # Can get posterior probs as well
        if get_pp:
            ref = get_voxel_data.references[reference + '_pp']
            _pp = pd.Series(ref.data[ind, :].ravel(), index=labels, name='pp')
            _pp = _pp * ref.stats['std'].values + ref.stats['mean'].values
            result = pd.concat([result, _pp], axis=1)
        return result

    except Exception:
        print traceback.format_exc()
        return False

@celery.task(base=NeurosynthTask)
def make_coactivation_map(x, y, z, r=6, min_studies=0.01):
    """ Generate a coactivation map on-the-fly for the given seed voxel. """
    try:
        dataset = make_coactivation_map.dataset
        ids = dataset.get_studies(peaks=[[x, y, z]], r=r)
        if len(ids) < 50:
            return False
        ma = meta.MetaAnalysis(dataset, ids, min_studies=min_studies)
        outdir = join(settings.IMAGE_DIR, 'coactivation')
        prefix = 'metaanalytic_coactivation_%s_%s_%s' % (str(x), str(y), str(z))
        ma.save_results(outdir, prefix, image_list=['pFgA_z_FDR_0.01'])
        return True
    except Exception, e:
        print traceback.format_exc()
        return False

@celery.task(base=NeurosynthTask)
def make_scatterplot(filename, analysis, base_id, reference='terms_full', outfile=None, n_voxels=None,
                     x_lab="Uploaded Image", y_lab=None, gene_masks=False):
    """ Generate a scatter plot displaying relationship between two images
    (typically a Neurosynth meta-analysis map and a retrieved image), where
    each voxel is an observation.
    Args:
        filename (string): local path to the retrieved image to plot on x axis
        analysis (string): name of the Neurosynth analysis to plot on y axis
        reference (string): the reference memmap image to use--e.g., terms,
            topics, etc.
        base_id (string): the UUID to base the output filename on
        outfile (string): if provided, the output file name
        n_voxels (int): if provided, the number of voxels to randomly sample
            (if None, all voxels are used)
        allow_nondecoder_analyses (boolean): whether to allow non-preloaded
            analyses (not currently implemented)
        x_lab (string): x axis label
        y_lab (string): y axis label
        gene_masks (boolean): when True, uses predetermined subcortical ROIs as
            masks; otherwise uses cortex vs. subcortex
    """
    try:
        # Get the data
        x = load_image(make_scatterplot.masker, filename)
        # y = get_decoder_analysis_data(make_scatterplot.dd, analysis)
        ref = make_scatterplot.references[reference]
        y = ref.data[:, ref.labels[analysis]]

        # Subsample random voxels
        if n_voxels is not None:
            voxels = np.random.choose(np.arange(len(x)), n_voxels)
            x, y = x[voxels], y[voxels]

        # Set filename if needed
        if outfile is None:
            outfile = join(settings.DECODING_SCATTERPLOTS_DIR, base_id + '_' +
                           analysis + '.png')

        # Generate and save scatterplot
        if y_lab is None:
            y_lab = '%s meta-analysis (z-score)' % analysis
        masks = make_scatterplot.masks
        
        if gene_masks:
            spatial_masks = [masks['subcortex']]
            region_labels = ['hippocampus', 'accumbens', 'amygdala', 'putamen']
            voxel_count_mask = masks['min4']
        else:
            spatial_masks = None
            region_labels = ['cortex', 'subcortex']
            voxel_count_mask = None

        region_masks = [masks[l] for l in region_labels]

        scatter(x, y, region_masks=region_masks, mask_labels=region_labels,
                unlabeled_alpha=0.15, alpha=0.5, fig_size=(12,12),
                palette='Set1', x_lab=x_lab, y_lab=y_lab, savefile=outfile,
                spatial_masks=spatial_masks, voxel_count_mask=voxel_count_mask)

    except Exception, e:
        print e
        print e.message
        return False


@celery.task(base=NeurosynthTask)
def run_metaanalysis(ids, name):
    """ Run a user-defined meta-analysis.
    Args:
        ids (list): list of PMIDs identifying studies to include in the
            meta-analysis
        name (string): name of the analysis; used in filename of output images
    """
    try:
        ma = meta.MetaAnalysis(run_metaanalysis.dataset, ids)
        outdir = join(settings.IMAGE_DIR, 'analyses')
        ma.save_results(outdir, name, image_list=['pFgA_z_FDR_0.01',
                        'pAgF_z_FDR_0.01'])
        return True
    except Exception, e:
        return False
