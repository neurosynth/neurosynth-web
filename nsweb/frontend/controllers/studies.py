from flask import Blueprint, render_template
from nsweb.models import Study
from nsweb.core import add_blueprint

bp = Blueprint('studies',__name__,url_prefix='/studies')

@bp.route('/')
def index():
    """Returns the studies page."""
    return render_template('studies/index.html.slim',studies=Study.query.count())

@bp.route('/<int:val>/')
def show(val):
    study = Study.query.get_or_404(val)
    viewer_settings = {
        'scale': 0.75,
        'images': [ { 
            'name': 'activations',
            'data': {
                'dims': [91, 109, 91],
                'peaks': [[p.x,p.y,p.z] for p in study.peaks]
            },
            'colorPalette': 'red'
        }],
        'options': { 'panzoomEnabled': 'false' },
    }
    return render_template('studies/show.html.slim', study=study, viewer_settings=viewer_settings)


# @bp.route('/download')
# gave up on this b/c issue is not image download I think?
# def download():
#     image = 'sadf'
#     response = make_response(image)
#     response.headers["Content-Disposition"] = "attachment; filename=asdf"
#     return response

add_blueprint(bp)

