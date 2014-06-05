from nsweb.core import add_blueprint
from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('locations',__name__,url_prefix='/locations')

@bp.route('/<string:val>/')
def show(val):
    x,y,z,radius = [int(i) for i in val.split('_')]
    viewer_settings = {
        'images': [ { 
            'name': 'activations',
            'data': {
                'dims': [91, 109, 91]
            },
            'colorPalette': 'red'
        }],
        'options': { 'panzoomEnabled': 'false' },
    }
    return render_template('locations/index.html.slim',radius=radius,x=x,y=y,z=z, viewer_settings=viewer_settings)

@bp.route('/')
def index():
    return redirect(url_for('locations.show',val='0_0_0_6'))

add_blueprint(bp)