from celery import Task
from nsweb.initializers import settings
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


def load_image(dataset, filename, save_resampled=True):
    """ Load an image, resampling into MNI space if needed. """
    filename = join(settings.DECODED_IMAGE_DIR, filename)
    img = nb.load(filename)
    if img.shape[:3] != (91, 109, 91):
        img = resample_img(img, target_affine=decode_image.anatomical.get_affine(), 
                            target_shape=(91, 109, 91), interpolation='nearest')
        if save_resampled:
            img.to_filename(filename)
    return dataset.masker.mask(img)

def get_decoder_feature_data(dd, feature):
    """ Get feature's data: check in the decoder DataFrame first, and if not found, 
    read from file (updating the in-memory DF). """
    if feature not in dd.columns:
            target_file = join(settings.IMAGE_DIR, 'features', feature + '_pFgA_z.nii.gz')
            if not exists(target_file):
                return False
            dd[feature] = load_image(make_scatterplot.dataset, target_file)
    return dd[feature].values

class NeurosynthTask(Task):

    @cached_property
    def dataset(self):
        return Dataset.load(settings.PICKLE_DATABASE)

    @cached_property
    def dd(self):  # decoding data
        return pd.read_msgpack(settings.DECODING_DATA)

    @cached_property
    def anatomical(self):
        f = join(settings.IMAGE_DIR, 'anatomical.nii.gz')
        return nb.load(f)

    @cached_property
    def masks(self):
        """ Return a dict of predefined region masks. """
        maps = {
            'cortex': join(IMAGE_DIR, 'Masks', 'cortex.nii'),
            'subcortex': join(IMAGE_DIR, 'Masks', 'subcortex_drewUpdated.nii'),
            'hippocampus': join(IMAGE_DIR, 'Masks', 'FSL_BHipp_thr0.nii.gz'),
            'accumbens': join(IMAGE_DIR, 'Masks', 'FSL_BNAcc_thr0.nii'),
            'amygdala': join(IMAGE_DIR, 'Masks', 'FSL_BAmyg_thr0.nii'),
            'putamen': join(IMAGE_DIR, 'Masks', 'FSL_BPut_thr0.nii.gz'),
            'min4': '/Volumes/data/AllenSynth/Data/Maps/voxel_counts_r6.nii.gz'
        }
        for m, img in maps.items():
            maps[m] = load_image(self.dataset, img)
        return maps

@celery.task(base=NeurosynthTask)
def count_studies(feature, threshold=0.001, **kwargs):
    """ Count the number of studies in the Dataset for a given feature. """
    ids = count_studies.dataset.get_ids_by_features(str(feature), threshold=threshold)
    return len(ids)

@celery.task(base=NeurosynthTask)
def save_uploaded_image(filename, **kwargs):
    pass
    
@celery.task(base=NeurosynthTask)
def decode_image(filename, **kwargs):
    """ Decode a retrieved image. """
    try:
        basefile = basename(filename)
        # Need to fix this--should probably add a "decode_id" field storing a UUID for 
        # any model that needs to be decoded but isn't an upload.
        uuid = 'gene_' + basefile.split('_')[2] if basefile.startswith('gene') else basefile[:32]
        dataset, dd = decode_image.dataset, decode_image.dd
        data = load_image(dataset, filename)

        # For genes, use only subcortical voxels
        if basefile.startswith('gene'):
            subcortex = decode_image.masks['subcortex']
            data = data[subcortex]
            dd = dd[subcortex,:]
            
        r = np.corrcoef(data.T, dd.values.T)[0,1:]
        outfile = join(settings.DECODING_RESULTS_DIR, uuid + '.txt')
        pd.Series(r, index=dd.columns).to_csv(outfile, sep='\t')
        return True
    except Exception, e:
        return False

@celery.task(base=NeurosynthTask)
def make_coactivation_map(x, y, z, r=6, min_studies=0.01):
    """ Generate a coactivation map on-the-fly for the given seed voxel. """
    try:
        dataset = make_coactivation_map.dataset
        ids = dataset.get_ids_by_peaks([[x, y, z]], r=r)
        if len(ids) < 50: return False
        ma = meta.MetaAnalysis(dataset, ids, min_studies=min_studies)
        outdir = join(settings.IMAGE_DIR, 'locations', 'coactivation')
        prefix = 'metaanalytic_coactivation_%s_%s_%s' % (str(x), str(y), str(z))
        ma.save_results(outdir, prefix, image_list=['pFgA_z_FDR_0.01'])
        return True
    except Exception, e:
        # print traceback.format_exc()
        return False

@celery.task(base=NeurosynthTask)
def make_scatterplot(filename, feature, base_id, outfile=None, n_voxels=None, allow_nondecoder_features=False, 
                    x_lab="Uploaded Image", y_lab=None, gene_masks=False):
    """ Generate a scatter plot displaying relationship between two images (typically a 
        Neurosynth meta-analysis map and a retrieved image), where each voxel is an observation. 
    Args:
        filename (string): the local path to the retrieved image to plot on x axis
        feature (string): the name of the Neurosynth feature to plot on y axis
        base_id (string): the UUID to base the output filename on
        outfile (string): if provided, the output file name
        n_voxels (int): if provided, the number of voxels to randomly sample (if None, 
            all voxels are used)
        allow_nondecoder_features (boolean): whether to allow non-preloaded features 
            (not currently implemented)
        x_lab (string): x axis label
        y_lab (string): y axis label
        gene_masks (boolean): when True, uses predetermined subcortical ROIs as masks; 
            otherwise uses cortex vs. subcortex
    """
    try:
        # Get the data
        x = load_image(make_scatterplot.dataset, filename)
        y = get_decoder_feature_data(make_scatterplot.dd, feature)

        # Subsample random voxels
        if n_voxels is not None:
            voxels = np.random.choose(np.arange(len(x)), n_voxels)
            x, y = x[voxels], y[voxels]

        # Set filename if needed
        if outfile is None:
            outfile = join(settings.DECODING_SCATTERPLOTS_DIR, base_id + '_' + feature + '.png')

        # Generate and save scatterplot
        if y_lab is None:
            y_lab='%s meta-analysis (z-score)' % feature
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

        scatter(x, y, region_masks=region_masks, mask_labels=region_labels, unlabeled_alpha=0.15,
                        alpha=0.5, fig_size=(12,12), palette='Set1', x_lab=x_lab, 
                        y_lab=y_lab, savefile=outfile, spatial_masks=spatial_masks,
                        voxel_count_mask=voxel_count_mask)

    except Exception, e:
        print e
        print e.message
        return False

@celery.task(base=NeurosynthTask)
def run_metaanalysis(ids, name):
    """ Run a user-defined meta-analysis.
    Args:
        ids (list): list of PMIDs identifying studies to include in the meta-analysis
        name (string): name of the analysis; used in filename of output images
    """
    try:
        ma = meta.MetaAnalysis(run_metaanalysis.dataset, ids)
        outdir = join(settings.IMAGE_DIR, 'analyses')
        ma.save_results(outdir, name, image_list=['pFgA_z_FDR_0.01', 'pAgF_z_FDR_0.01'])
        return True
    except Exception, e:
        return False

