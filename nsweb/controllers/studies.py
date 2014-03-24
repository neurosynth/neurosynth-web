from nsweb.models import Study
from nsweb.blueprints import add_blueprint
from flask import Blueprint, render_template

studies = Blueprint('studies', __name__, 
    url_prefix='/studies')

@studies.route('/')
def index():
    return render_template('studies/index.html', studies=Study.query.all())

@studies.route('/<id>')
def show(id):
    return render_template('studies/show.html', study=Study.query.get_or_404(id))

add_blueprint(studies)
