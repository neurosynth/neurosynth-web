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
    return render_template('studies/show.html.slim', study=Study.query.get_or_404(id))

add_blueprint(bp)