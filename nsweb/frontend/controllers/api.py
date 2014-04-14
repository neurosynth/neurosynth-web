from nsweb.core import add_blueprint
from flask import Blueprint, redirect, jsonify, url_for
from nsweb.models import *

bp = Blueprint('apis',__name__,url_prefix='/api')

@bp.route('/studies/<int:val>/')
def studies_api(val):
    data = [ ['<a href={0}>{1}</a>'.format(url_for('features.show',val=f.feature_val),f.feature.feature),
              f.frequency,
              ] for f in Study.query.get_or_404(val).frequencies]
#     data=dumps({'aadata':data})
    data=jsonify(aaData=data)
    return data

@bp.route('/features/<string:name>/')
def find_api_feature(name):
    """ If the passed val isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    """
    val = Feature.query.filter_by(feature=name).first().id
    return redirect(url_for('features.api',id=val))

@bp.route('/features/<int:val>/')
def features_api(val):
    data = [ ['<a href={0}>{1}</a>'.format(url_for('studies.show',val=str(f.pmid)),f.study.title),
              f.study.authors,
              f.study.journal,
              f.frequency,
              ] for f in Feature.query.get_or_404(val).frequencies]
#     data=dumps({'aadata':data})
    data=jsonify(aaData=data)
    return data

@bp.route('/locations/<string:val>')
def locations_api(val):
    x,y,z,radius = [int(i) for i in val.split('_')]
    points = Peak.closestPeaks(radius,x,y,z)
    data = [ [p.study.title, p.study.authors, p.study.journal] for p in points]
    return jsonify(aaData=data)

add_blueprint(bp)
