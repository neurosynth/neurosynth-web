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
    images=''
    for i in feature.images:
#        if i.visible:
        reverse=i.label.find('reverse')
        images+= '{{"name":"{0}","id":{1},"download":"/images/{1}","intent":"{2}","visible":{3},"colorPalette":{4}}},'.format(i.name,
                                                                                                                          i.id,
                                                                                                                          (i.stat + ' :').capitalize(),
                                                                                                                          'true' if reverse else'false',
                                                                                                                          '"red"' if reverse else '"blue"')
    return render_template('features/show.html.slim', feature=feature.feature, images=images)

@bp.route('/<string:name>/')
def find_feature(name):
    """ If the passed ID isn't numeric, assume it's a feature name,
    and retrieve the corresponding numeric ID. 
    """
    val = Feature.query.filter_by(feature=name).first().id
    return redirect(url_for('features.show',val=val))

add_blueprint(bp)