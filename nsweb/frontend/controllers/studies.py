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
    peaks =[{"x": p.x,"y":p.y,"z":p.z} for p in study.peaks]
    return render_template('studies/show.html.slim', study=study, peaks=peaks)

add_blueprint(bp)

