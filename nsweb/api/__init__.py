from nsweb.core import add_blueprint, app
from flask import Blueprint, render_template
from flask_swagger import swagger

bp = Blueprint('apis', __name__, url_prefix='/api')

from nsweb.api.operations import *

add_blueprint(bp)

@bp.route('/')
def index():
    return render_template('home/api.html.slim')

@bp.route('/swagger.json')
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Neurosynth API"
    return jsonify(swag)
