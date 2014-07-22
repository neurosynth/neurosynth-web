from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from nsweb.models.locations import Location
from nsweb.models.peaks import Peak
import simplejson as json
from flask_sqlalchemy import sqlalchemy
from nsweb.initializers import settings
from os.path import join, exists

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
    if location is not None:
        images = [{
            'id': img.id,
            'name': img.label,
            'colorPalette': 'yellow' if 'coactivation' in img.label else 'red',
            'url': '/images/%s' % img.id,
            'visible': 0 if 'coactivation' in img.label else 1
        } for img in location.images if img.display]
    else:
        images = []
    return jsonify(data=images)


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

add_blueprint(bp)
