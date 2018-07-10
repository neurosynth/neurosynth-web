
# Test correlation approaches
import numpy as np
import pandas as pd
import nibabel as nb
from glob import glob
import time
import random
import os
from neurosynth import Masker
# from neurosynth.analysis.stats import pearson
import tempfile
import sys

import numpy as np

# Code from http://stackoverflow.com/questions/20983882/efficient-dot-products-of-large-memory-mapped-arrays
import numpy as np


def _block_slices(dim_size, block_size):
    """Generator that yields slice objects for indexing into
    sequential blocks of an array along a particular axis
    """
    count = 0
    while True:
        yield slice(count, count + block_size, 1)
        count += block_size
        if count > dim_size:
            raise StopIteration


def blockwise_dot(A, B, max_elements=int(2**20), out=None):
    """
    Computes the dot product of two matrices in a block-wise fashion.
    Only blocks of `A` with a maximum size of `max_elements` will be
    processed simultaneously.
    """

    B = np.atleast_2d(B).T
    m,  n = A.shape
    n1, o = B.shape

    if n1 != n:
        raise ValueError('matrices are not aligned')

    if A.flags.f_contiguous:
        # prioritize processing as many columns of A as possible
        max_cols = max(1, max_elements / m)
        max_rows = max_elements / max_cols

    else:
        # prioritize processing as many rows of A as possible
        max_rows = max(1, max_elements / n)
        max_cols = max_elements / max_rows

    if out is None:
        out = np.empty((m, o), dtype=np.result_type(A, B))
    elif out.shape != (m, o):
        raise ValueError('output array has incorrect dimensions')

    for mm in _block_slices(m, max_rows):
        out[mm, :] = 0
        for nn in _block_slices(n, max_cols):
            A_block = A[mm, nn].copy()  # copy to force a read
            out[mm, :] += np.dot(A_block, B[nn, :])
            del A_block

    return out


def pearson(x, y):
    """ Correlates row vector x with each row vector in 2D array y. """
    data = np.vstack((x, y))
    ms = data.mean(axis=1)[(slice(None, None, None), None)]
    datam = data - ms

    def ss(arr, axis=None):
        return np.sum(arr**2, axis=axis)

    datass = np.sqrt(ss(datam, axis=1))
    temp = np.dot(datam[1:], datam[0].T)
    rs = temp / (datass[1:] * datass[0])
    return rs


f = '/tmp/memmap_small.dat'
# Get mask
masker = Masker('/data/images/anatomical.nii.gz')

n_maps = 10000
n_files = 1

labels = []
# Load images
t0 = time.time()
z_maps = glob('/data/images/analyses/*specificity_z_FDR*nii.gz')[:n_maps]
n_maps = len(z_maps)
for z in z_maps:
    labels.append(os.path.basename(z).split('_')[0])

# random.shuffle(z_maps)
# n_vox = np.sum(masker.get_current_mask())
n_maps = len(z_maps)
n_sampled = 20000


def make_memmap():

    # Randomly draw N voxels and save indices to drive
    sample = np.random.choice(np.arange(228453), n_sampled, replace=False)
    print sample
    np.save('sample_indices.npy', sample)

    # f = tempfile.mktemp()
    res = np.memmap(f, dtype='float32', mode='w+', shape=(n_sampled, n_maps))

    for i, img in enumerate(z_maps):
        img_data = masker.mask(img)[sample]
        res[:, i] = (img_data - img_data.mean())/img_data.std()
    t1 = time.time()
    print "Time to load all images: %.2f seconds" % (t1 - t0)
    del res


def time_corr(term):
    sample = np.load('sample_indices.npy')
    # print sample
    # random.shuffle(z_maps)
    t0 = time.time()
    res = np.memmap(f, dtype='float32', mode='r', shape=(n_sampled, n_maps))
    t1 = time.time()
    # print "Time to reload memmap: %.2f" % (t1 - t0)
    t0 = time.time()
    results = np.zeros((n_files, n_maps))
    # to_compare = np.random.choice(np.arange(n_maps), 1, replace=False)
    # print to_compare
    target = labels.index(term)
    if not target:
        raise ValueError("No term %s found!" % term)
    # for (i, img) in enumerate(to_compare):
    for (i, img) in enumerate([target]):
        # for (i, img) in enumerate(z_maps[300:301]):
        data = masker.mask(z_maps[img])[sample]
        data = (data - data.mean())/data.std()
        coefs = np.zeros(n_maps)
        # for j in range(len(z_maps)):
        results = np.dot(res.T, data)/n_sampled
    t1 = time.time()
    print results.shape
    results = pd.Series(np.squeeze(results), index=labels)
    # print results[~np.isnan(results)].max()
    print results.order(ascending=False)[:50]
    print "Time to correlate %d images with rest: %.2f seconds" % (n_files, t1 - t0)
    # os.unlink(f)


# make_memmap()
time_corr(sys.argv[1])
