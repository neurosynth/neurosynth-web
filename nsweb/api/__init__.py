from nsweb.core import app
from flask import Blueprint, render_template
from flask_swagger import swagger

bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

from nsweb.api.operations import *
from nsweb.api.datatables import *


@bp.route('/')
def index():
    return render_template('home/api.html')

@bp.route('/swagger.json')
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Neurosynth API"
    return jsonify(swag)
