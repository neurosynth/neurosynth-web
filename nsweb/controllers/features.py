from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort
from nsweb.models import Feature
from nsweb.core import add_blueprint
from flask.helpers import url_for
import simplejson as json
import re

bp = Blueprint('features',__name__,url_prefix='/features')
 

def find_feature(val):
    ''' Retrieve feature by either id (when int) or name (when string) '''
    feature = Feature.query.get(val) if re.match('\d+$', val) else Feature.query.filter_by(name=val).first()
    if feature is None: abort(404)
    return feature
    
@bp.route('/')
def index():
    return render_template('features/index.html.slim')
 
@bp.route('/feature_names/')
def get_feature_names():
    names = [f.name for f in Feature.query.all()]  # optimize this later--select only names
    return jsonify(data=names)

@bp.route('/<string:val>/')
def show(val):
    feature = find_feature(val)
    n_studies = feature.frequencies.count()
    return render_template('features/show.html.slim', feature=feature.name, n_studies=n_studies)

@bp.route('/<string:val>/images')
def get_images(val):
    feature = find_feature(val)
    images = [{
        'id': img.id,
        'name': img.label,
        'colorPalette': 'red' if 'reverse' in img.label else 'blue',
        # "intent": (img.stat + ':').capitalize(),
        'url': '/images/%s' % img.id,
        'visible': 1 if 'reverse' in img.label else 0,
        'download': '/images/%s' % img.id,
        'intent': 'z-score'
    } for img in feature.images if img.display]
    return jsonify(data=images)

@bp.route('/<string:val>/images/reverseinference/')
def get_reverse_inference_image(val):
    # Horrible hacks here to serve just reverse inference images with or 
    # without FDR; totally mucks up API pattern, so clean up later.
    feature = find_feature(val)
    fdr = ('nofdr' not in request.args.keys())
    img = [i for i in feature.images if 'reverse' in i.label][0]
    from nsweb.controllers import images
    return images.download(img.id, fdr)

@bp.route('/<string:val>/studies')
def get_studies(val):
    feature = find_feature(val) 
    if 'dt' in request.args:
        data = []
        for f in feature.frequencies:
            s = f.study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',val=s.pmid),s.title)
            data.append([link, s.authors, s.journal, round(f.frequency, 3)])
        data = jsonify(data=data)
    else:
        data = jsonify(studies=[s.pmid for s in feature.studies])
    return data

add_blueprint(bp)

