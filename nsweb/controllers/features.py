from flask import Blueprint, render_template, redirect, url_for
from nsweb.models import Feature
from nsweb.core import add_blueprint
from flask.helpers import url_for

bp = Blueprint('features',__name__,url_prefix='/features')
 
@bp.route('/')
def index():
    return render_template('features/index.html.slim', features=Feature.query.all())
 
@bp.route('/<int:val>/')
def show(val):
    feature = Feature.query.get_or_404(val)
    reverse=False
    viewer_settings = {
                       'images': [ { 
                                    'name': i.label,
                                    'id': i.id,
                                    'download': url_for('images.download',val=i.id),#"/images/{}/".format(i.id),
                                    'intent': (i.stat + ' :').capitalize,
                                    'visible': True,
                                    'colorPalette': 'red',
                                    } for i in feature.images],
                       'options': { 'panzoomEnabled': 'false' },
                       }
    return render_template('features/show.html.slim', feature=feature.name, viewer_settings=viewer_settings)

@bp.route('/<string:name>/')
def find_feature(name):
    """ If the passed ID isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    """
    val = Feature.query.filter_by(feature=name).first().id
    return redirect(url_for('features.show',val=val))

add_blueprint(bp)