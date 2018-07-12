from nsweb.core import cache
from flask import (Blueprint, render_template, url_for, request, jsonify,
                   redirect)
from flask_user import current_user
from nsweb.models.locations import Location
from nsweb.models.images import LocationImage
from nsweb.models.peaks import Peak
from flask_sqlalchemy import sqlalchemy
from nsweb.initializers import settings
from os.path import join, exists
from nsweb import tasks
from nsweb.core import db, app
from nsweb.controllers.decode import decode_analysis_image, get_voxel_data
from nsweb.controllers.images import get_decoding_data
import pandas as pd
import numpy as np
from collections import defaultdict


bp = Blueprint('locations', __name__, url_prefix='/locations')


class RedirectedLocation(Exception):

    def __init__(self, url, status_code=None):
        Exception.__init__(self)
        self.url = url
        if status_code is None:
            status_code = 302
        self.status_code = status_code


@app.errorhandler(RedirectedLocation)
def handle_redirected_location(error):
    return redirect(error.url, error.status_code)


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string.decode('utf-8') + \
        str(current_user.is_authenticated)


def get_params(val=None, location=False):
    ''' Extract x/y/z and radius from either URL route or query parameters '''
    if val is None:
        x = int(request.args.get('x', 0) or 0)
        y = int(request.args.get('y', 0) or 0)
        z = int(request.args.get('z', 0) or 0)
        radius = int(request.args.get('r', 6) or 6)

    else:
        params = val.split('_')
        if len(params) == 3:
            params.append(6)
        x, y, z, radius = [int(val) for val in params]

    # Check validity and redirect if necessary
    check_xyz(x, y, z)

    if radius > 20:
        radius = 20
    if location:
        return Location.query.filter_by(x=x, y=y, z=z).first()
    return (x, y, z, radius)


def check_xyz(x, y, z):
    # Round all x/y/z values to nearest even number
    _x, _y, _z = map(lambda v: int(round(v/2.)*2), [x, y, z])
    if (x, y, z) != (_x, _y, _z):
        new_args = dict(request.args.items() +
                        {'x': _x, 'y': _y, 'z': _z}.items())
        url = url_for(request.url_rule.endpoint, **new_args)
        raise RedirectedLocation(url)


@bp.route('/<string:val>/images')
@bp.route('/images/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_images(val=None):
    location = get_params(val, location=True)
    if location is None:
        x, y, z, r = get_params(val)
        location = make_location(x, y, z)

    images = [{
        'id': img.id,
        'name': img.label,
        'colorPalette': 'yellow' if 'coactivation' in img.label else 'red',
        'url': '/images/%s' % img.id,
        'visible': 0 if 'coactivation' in img.label else 1,
        'download': '/images/%s' % img.id,
        'description': img.description,
        'intent': img.stat,
        'positiveThreshold': 0 if 'coactivation' in img.label else 0.2,
        'negativeThreshold': 0 if 'coactivation' in img.label else -0.2
    } for img in location.images if img.display]
    db.session.remove()
    return jsonify(data=images)


@bp.route('/<string:val>/compare/')
@bp.route('/compare/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def compare_location(val=None, decimals=2):
    """ Compare this voxel to various image sets using various approaches.
    Currently returns correlations between the coactivation/functional
    connectivity maps seeded at this voxel and all images in a given term set,
    plus activation data at this location.
    """
    x, y, z, radius = get_params(val)
    location = get_params(val, location=True) or make_location(x, y, z)
    ma = list(zip(*get_decoding_data(location.images[0].id, get_json=False)))
    fc = list(zip(*get_decoding_data(location.images[1].id, get_json=False)))
    ma = pd.Series(ma[1], index=ma[0], name='ma')
    fc = pd.Series(fc[1], index=fc[0], name='fc')
    # too many gene maps to slice into, so return NAs
    ref_type = request.args.get('set', 'terms_20k').split('_')[0]
    if ref_type != 'genes':
        vals = get_voxel_data(x, y, z, ref_type, get_json=False)
    else:
        vals = pd.Series([np.nan])

    data = pd.concat([ma, fc, vals], axis=1)
    data = data.apply(lambda x: np.round(x, decimals)).reset_index()
    data = data.fillna('-')
    data = data[['index', 'z', 'pp', 'fc', 'ma']]
    return jsonify(data=data.values.tolist())


@bp.route('/<string:val>/studies/')
@bp.route('/studies/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_studies(val=None):
    x, y, z, radius = get_params(val)
    points = Peak.closestPeaks(radius, x, y, z)

    # Track number of peaks and study details for each found study,
    # keeping only peaks that haven't been previously seen for current
    # study/x/y/z combination.
    seen = {}
    study_counts = defaultdict(list)
    for p in points:
        key = hash((p.pmid, round(p.x, 2), round(p.y, 2), round(p.z, 2)))
        if key in seen:
            next
        study_counts[p.pmid].append(p)
        seen[key] = 1

    if 'dt' in request.args:
        data = []
        for pmid, peaks in study_counts.items():
            s = peaks[0].study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',
                                                        val=pmid), s.title)
            data.append([link, s.authors, s.journal, len(peaks)])
    else:
        data = [{'pmid': pmid, 'peaks': len(peaks)}
                for pmid, peaks in study_counts.items()]
    return jsonify(data=data)


@bp.route('/')
@bp.route('/<string:val>/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def show(val=None):
    x, y, z, radius = get_params(val)
    return render_template('locations/index.html', radius=radius, x=x,
                           y=y, z=z)


def make_location(x, y, z):

    location = Location(x, y, z)

    # Add Neurosynth coactivation image if it exists
    filename = 'metaanalytic_coactivation_%d_%d_%d_association-test_z_FDR_0.01.nii.gz' % (
        x, y, z)
    filename = join(settings.IMAGE_DIR, 'coactivation', filename)
    if not exists(filename):
        tasks.make_coactivation_map.delay(x, y, z).wait()
    if exists(filename):
        ma_image = LocationImage(
            name='Meta-analytic coactivation for seed (%d, %d, %d)' % (
                x, y, z),
            image_file=filename,
            label='Meta-analytic coactivation',
            stat='z-score',
            display=1,
            download=1,
            description='This image displays regions coactivated with the seed'
            ' region across all studies in the Neurosynth database. It '
            'represents meta-analytic coactivation rather than time '
            'series-based connectivity.'
        )
        location.images.append(ma_image)

    # Add Yeo FC image if it exists
    filename = join(settings.IMAGE_DIR, 'fcmri',
                    'functional_connectivity_%d_%d_%d.nii.gz' % (x, y, z))
    if exists(filename):
        fc_image = LocationImage(
            name='YeoBucknerFCMRI for seed (%d, %d, %d)' % (x, y, z),
            image_file=filename,
            label='Functional connectivity',
            stat='corr. (r)',
            description='This image displays resting-state functional '
            'connectivity for the seed region in a sample of 1,000 subjects. '
            'To reduce blurring of signals across cerebro-cerebellar and '
            'cerebro-striatal boundaries, fMRI signals from adjacent cerebral '
            'cortex were regressed from the cerebellum and striatum. For '
            'details, see '
            '<a href="http://jn.physiology.org/content/106/3/1125.long">Yeo et'
            'al (2011)</a>, <a href="http://jn.physiology.org/cgi/pmidlookup?'
            'view=long&pmid=21795627">Buckner et al (2011)</a>, and '
            '<a href="http://jn.physiology.org/cgi/pmidlookup?view=long&'
            'pmid=22832566">Choi et al (2012)</a>.',
            display=1,
            download=1
        )
        location.images.append(fc_image)

    db.session.add(location)
    db.session.commit()

    # Decode both images
    for img in location.images:
        decode_analysis_image(img.id)

    return location
