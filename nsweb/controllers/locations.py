from nsweb.core import add_blueprint, cache
from flask import Blueprint, render_template, url_for, request, jsonify
from nsweb.models.locations import Location
from nsweb.models.images import LocationImage
from nsweb.models.peaks import Peak
import simplejson as json
from flask_sqlalchemy import sqlalchemy
from nsweb.initializers import settings
from os.path import join, exists
from nsweb.tasks import make_coactivation_map
from nsweb.core import db
from nsweb.controllers.decode import decode_analysis_image, get_voxel_data
from nsweb.controllers.images import get_decoding_data
import pandas as pd
import numpy as np


bp = Blueprint('locations', __name__, url_prefix='/locations')


def get_params(val=None, location=False):
    ''' Extract x/y/z and radius from either URL route or query parameters '''
    if val is None:
        x = int(request.args.get('x', 0))
        y = int(request.args.get('y', 0))
        z = int(request.args.get('z', 0))
        radius = int(request.args.get('r', 6))
    else:
        params = [int(e) for e in val.split('_')]
        if len(params) == 3:
            params.append(6)
        x, y, z, radius = params

    if radius > 20:
        radius = 20
    if location:
        return Location.query.filter_by(x=x, y=y, z=z).first()
    return (x, y, z, radius)


@bp.route('/')
@bp.route('/<string:val>/')
def show(val=None):
    x, y, z, radius = get_params(val)
    return render_template('locations/index.html.slim', radius=radius, x=x,
                           y=y, z=z)


@bp.route('/<string:val>/images')
def get_images(val):
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
@cache.memoize(timeout=3)
def compare_location(val, decimals=2):
    x, y, z, radius = get_params(val)
    location = get_params(val, location=True) or make_location(x, y, z)
    ma = zip(*get_decoding_data(location.images[0].id, get_json=False))
    fc = zip(*get_decoding_data(location.images[1].id, get_json=False))
    ma = pd.Series(ma[1], index=ma[0])
    fc = pd.Series(fc[1], index=fc[0])
    # too many gene maps to slice into, so return NAs
    ref_type = request.args.get('set', 'terms_20k').split('_')[0]
    if ref_type != 'genes':
        vals = get_voxel_data(x, y, z, '%s_full' % ref_type, get_json=False)
    else:
        vals = pd.Series([np.nan])

    data = pd.concat([ma, fc, vals], axis=1)
    data = data.apply(lambda x: np.round(x, decimals)).reset_index()
    data = data.fillna('-')
    return jsonify(data=data.values.tolist())


@bp.route('/<string:val>/studies')
def get_studies(val):
    x, y, z, radius = get_params(val)
    points = Peak.closestPeaks(radius, x, y, z)
    # prevents duplicate studies
    points = points.group_by(Peak.pmid)
    # counts duplicate peaks
    points = points.add_columns(sqlalchemy.func.count(Peak.id))

    if 'dt' in request.args:
        data = []
        for p in points:
            s = p[0].study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',
                                                        val=s.pmid), s.title)
            data.append([link, s.authors, s.journal, p[1]])
        data = jsonify(data=data)
    else:
        data = [{'pmid': p[0].study.pmid, 'peaks':p[1]} for p in points]
        data = jsonify(data=data)
    return data


# @bp.route('/<string:val>/analyses')
# def get_analyses(val):
#     x, y, z, radius = get_params(val)
#     f = join(settings.LOCATION_FEATURE_DIR, '%d_%d_%d_analyses.txt' % (x,y,z))
#     return open(f).read() if exists(f) else '{"data":[]}'


def make_location(x, y, z):

    location = Location(x, y, z)

    # Add Neurosynth coactivation image if it exists
    filename = 'metaanalytic_coactivation_%d_%d_%d_pFgA_z_FDR_0.01.nii.gz' % (
        x, y, z)
    filename = join(settings.IMAGE_DIR, 'coactivation', filename)
    if not exists(filename):
        result = make_coactivation_map.delay(x, y, z).wait()
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
            'view=long&pmid=21795627>Buckner et al (2011)</a>, and '
            '<a href="http://jn.physiology.org/cgi/pmidlookup?view=long&'
            'pmid=22832566">Choi et al (2012)</a>.',
            display=1,
            download=1
        )
        location.images.append(fc_image)

    db.session.add(location)
    db.session.commit()

    # Decode both images
    decode_analysis_image(ma_image.id)
    decode_analysis_image(fc_image.id)

    return location

add_blueprint(bp)
