from flask import Blueprint, render_template
from nsweb.models.studies import Study


bp = Blueprint('studies', __name__, url_prefix='/studies')


@bp.route('/')
def index():
    """Returns the studies page."""
    return render_template('studies/index.html',
                           studies=Study.query.count())


@bp.route('/<int:val>/')
def show(val):
    study = Study.query.get_or_404(val)
    return render_template('studies/show.html', study=study)
