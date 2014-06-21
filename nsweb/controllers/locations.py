from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, url_for
from nsweb.models.locations import Location
import simplejson as json

bp = Blueprint('locations',__name__,url_prefix='/locations')

@bp.route('/<string:val>/')
def show(val):
    x,y,z,radius = [int(i) for i in val.split('_')]
    if radius > 20: radius = 20
    location = Location.query.filter_by(x=x,y=y,z=z)
    rev_inf = '/data/neurosynth/data/locations/images/' + '_'.join([str(i) for i in [x, y, z]]) + '_pFgA_z_FDR_0.05'
    images = json.dumps([{
      'id': 'meh', 
      'name':'[%s, %s, %s] coactivation (reverse inference)' % (x,y,z), 
      'colorPalette': 'red', 
      'cache': True, 
      'url': rev_inf }])
    return render_template('locations/index.html.slim', radius=radius, x=x, y=y, z=z, images=images)

@bp.route('/')
def index():
    return redirect(url_for('locations.show',val='0_0_0_6'))

add_blueprint(bp)
