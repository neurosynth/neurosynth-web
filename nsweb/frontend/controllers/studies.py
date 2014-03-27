from flask import Blueprint, render_template
from nsweb.models import Study
from nsweb.core import add_blueprint

bp = Blueprint('home',__name__)

@bp.route('/studies/')
def index():
    """Returns the studies page."""
    return render_template('studies/index.html.slim',studies=Study.query.count())

@bp.route('/studies/<int:id>')
def show(id):
    study = Study.query.get_or_404(id)
    viewer_settings = {
        'scale': 0.75,
        'images': [ { 
            'name': 'activations',
            'data': {
                'dims': [91, 109, 91],
                'peaks': study.peaks 
            },
            'colorPalette': 'red'
        }],
        'options': { 'panzoomEnabled': False }
    }
    return render_template('studies/show.html.slim', study=study, viewer_settings=viewer_settings)

add_blueprint(bp)