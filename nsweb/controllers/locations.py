from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from nsweb.models import Location, LocationImage
from nsweb.models.peaks import Peak
import simplejson as json
from flask_sqlalchemy import sqlalchemy
from nsweb.initializers import settings
from os.path import join, exists
from nsweb.tasks import make_coactivation_map
from nsweb.controllers.images import send_nifti
from nsweb.core import db

bp = Blueprint('locations',__name__,url_prefix='/locations')


def get_params(val=None, location=False):
    ''' Extract x/y/z and radius from either URL route or query parameters '''
    if val is None:
        x = int(request.args.get('x', 0))
        y = int(request.args.get('y', 0))
        z = int(request.args.get('z', 0))
        radius = int(request.args.get('r', 6))
    else:
        params = [int(e) for e in val.split('_')]
        if len(params) == 3: params.append(6)
        x, y, z, radius = params
        
    if radius > 20: radius = 20
    if location:
        return Location.query.filter_by(x=x,y=y,z=z).first()
    return (x, y, z, radius)


@bp.route('/')
@bp.route('/<string:val>')
def show(val=None):
    x, y, z, radius = get_params(val)
    return render_template('locations/index.html.slim', radius=radius, x=x, y=y, z=z)


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
        'download': img.download,
        'description': img.description,
        'intent': img.stat,
        'positiveThreshold': 0 if 'coactivation' in img.label else 0.2,
        'negativeThreshold': 0 if 'coactivation' in img.label else -0.2
    } for img in location.images if img.display]

    db.session.remove()
    return jsonify(data=images)


# @bp.route('/<string:val>/coactivation')
# def get_coactivation_image(val):
#     x, y, z, r = get_params(val)
#     filename = 'metaanalytic_coactivation_%s_%s_%s_pFgA_z.nii.gz' % (str(x), str(y), str(z))
#     filename = join(settings.IMAGE_DIR, 'locations', 'coactivation', filename)
#     if not exists(filename):
#         result = make_coactivation_map.delay(int(x), int(y), int(z)).wait()
#     if exists(filename):
#         return send_nifti(filename)
#     return abort(404)


@bp.route('/<string:val>/studies')
def get_studies(val):
    x, y, z, radius = get_params(val)
    points = Peak.closestPeaks(radius,x,y,z)
    points = points.group_by(Peak.pmid) #prevents duplicate studies
    points = points.add_columns(sqlalchemy.func.count(Peak.id)) #counts duplicate peaks
    
    if 'dt' in request.args:
        data = []
        for p in points:
            s = p[0].study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',val=s.pmid),s.title)
            data.append([link, s.authors, s.journal,p[1]])
        data = jsonify(data=data)
    else:
        data = [{'pmid':p[0].study.pmid,'peaks':p[1] } for p in points]
        data = jsonify(data=data)
    return data

@bp.route('/<string:val>/features')
def get_features(val):
    x, y, z, radius = get_params(val)
    f = join(settings.LOCATION_FEATURE_DIR, '%d_%d_%d_features.txt' % (x,y,z))
    return open(f).read() if exists(f) else '{"data":[]}'

def make_location(x, y, z):

    location = Location(x, y, z)
    location.images = []

    # Add Neurosynth coactivation image if it exists
    filename = 'metaanalytic_coactivation_%d_%d_%d_pFgA_z_FDR_0.01.nii.gz' % (x, y, z)
    filename = join(settings.IMAGE_DIR, 'locations', 'coactivation', filename)
    if not exists(filename):
        result = make_coactivation_map.delay(x, y, z).wait()
    if exists(filename):
        location.images.append(LocationImage(
            name = 'Meta-analytic coactivation for seed (%d, %d, %d)' % (x, y, z),
            image_file = filename,
            label = 'Meta-analytic coactivation',
            stat = 'z-score',
            display = 1,
            download = 1,
            description = 'This image displays regions coactivated with the seed region across all studies in the Neurosynth database. It represents meta-analytic coactivation rather than time series-based connectivity.'
        ))

    # Add Yeo FC image if it exists
    filename = join('/data/neurosynth/data/locations', 'fcmri', 'functional_connectivity_%d_%d_%d.nii.gz' % (x, y, z))
    if exists(filename):
        location.images.append(LocationImage(
            name='YeoBucknerFCMRI for seed (%d, %d, %d)' % (x, y, z),
            image_file = filename,
            label = 'Functional connectivity',
            stat = 'corr. (r)',
            description = "This image displays resting-state functional connectivity for the seed region in a sample of 1,000 subjects. To reduce blurring of signals across cerebro-cerebellar and cerebro-striatal boundaries, fMRI signals from adjacent cerebral cortex were regressed from the cerebellum and striatum. For details, see <a href='http://jn.physiology.org/content/106/3/1125.long'>Yeo et al (2011)</a>, <a href='http://jn.physiology.org/cgi/pmidlookup?view=long&pmid=21795627'>Buckner et al (2011)</a>, and <a href='http://jn.physiology.org/cgi/pmidlookup?view=long&pmid=22832566'>Choi et al (2012)</a>.",
            display = 1,
            download = 1
        ))

    db.session.add(location)
    db.session.commit()
    return location

add_blueprint(bp)
