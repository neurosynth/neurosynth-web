from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort
from nsweb.models import Analysis
from nsweb.core import add_blueprint
from flask.helpers import url_for
import simplejson as json
import re

bp = Blueprint('analyses',__name__,url_prefix='/analyses')
 

def find_analysis(val):
    ''' Retrieve analysis by either id (when int) or name (when string) '''
    return Analysis.query.get(val) if re.match('\d+$', val) else Analysis.query.filter_by(name=val).first()
    
@bp.route('/')
def index():
    return render_template('analyses/index.html.slim')
 
@bp.route('/analysis_names/')
def get_analysis_names():
    names = [f.name for f in Analysis.query.all()]  # optimize this later--select only names
    return jsonify(data=names)

@bp.route('/<string:val>/')
def show(val):
    analysis = find_analysis(val)
    if analysis is None:
        return render_template('analyses/missing.html.slim', analysis=val)
    n_studies = analysis.frequencies.count()
    return render_template('analyses/show.html.slim', analysis=analysis.name, n_studies=n_studies)

@bp.route('/<string:val>/images')
def get_images(val):
    analysis = find_analysis(val)
    images = [{
        'id': img.id,
        'name': img.label,
        'colorPalette': 'red' if 'reverse' in img.label else 'blue',
        # "intent": (img.stat + ':').capitalize(),
        'url': '/images/%s' % img.id,
        'visible': 1 if 'reverse' in img.label else 0,
        'download': '/images/%s' % img.id,
        'intent': 'z-score'
    } for img in analysis.images if img.display]
    return jsonify(data=images)

@bp.route('/<string:val>/images/reverseinference/')
def get_reverse_inference_image(val):
    # Horrible hacks here to serve just reverse inference images with or 
    # without FDR; totally mucks up API pattern, so clean up later.
    analysis = find_analysis(val)
    fdr = ('nofdr' not in request.args.keys())
    img = [i for i in analysis.images if 'reverse' in i.label][0]
    from nsweb.controllers import images
    return images.download(img.id, fdr)

@bp.route('/<string:val>/studies')
def get_studies(val):
    analysis = find_analysis(val)
    if 'dt' in request.args:
        data = []
        for f in analysis.frequencies:
            s = f.study
            link = '<a href={0}>{1}</a>'.format(url_for('studies.show',val=s.pmid),s.title)
            data.append([link, s.authors, s.journal, round(f.frequency, 3)])
        data = jsonify(data=data)
    else:
        data = jsonify(studies=[s.pmid for s in analysis.studies])
    return data

add_blueprint(bp)

