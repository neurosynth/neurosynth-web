from flask import Blueprint, render_template, request, redirect, url_for
from nsweb.models import Feature
from nsweb.core import apimanager, add_blueprint, app
from flask.json import jsonify, dumps

bp = Blueprint('features',__name__,url_prefix='/features')
 
@bp.route('/')
def index():
    return render_template('features/index.html.slim', features=Feature.query.all())
 
@bp.route('/<int:val>/')
def show(val):
    feature = Feature.query.get_or_404(val)
    return render_template('features/show.html.slim', feature=feature.feature)

@bp.route('/<string:name>/')
def find_feature(name):
    """ If the passed ID isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    """
    id = Feature.query.filter_by(feature=name).first().id
    return redirect(url_for('features.show',id=id))

add_blueprint(bp)