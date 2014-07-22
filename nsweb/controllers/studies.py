from flask import Blueprint, render_template, jsonify
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
    return render_template('studies/show.html.slim', study=study)

@bp.route('/<int:val>/tables')
def get_tables(val):
    study = Study.query.get_or_404(val)
    colors = ['blue', 'red', 'yellow', 'green', 'purple', 'brown']
    tables = {}
    for p in study.peaks:
        if p.table not in tables:
            tables[p.table] = {
                'name': 'table_' + str(p.table),
                'colorPalette': colors.pop(0),
                'data': {
                    'dims': [91,109,91],
                    'peaks': [],
                }
            }
        tables[p.table]['data']['peaks'].append({"x": p.x,"y":p.y,"z":p.z})
    # print [[t['name'], t['colorPalette']] for t in tables.values()]
    return jsonify(data=tables.values())

add_blueprint(bp)