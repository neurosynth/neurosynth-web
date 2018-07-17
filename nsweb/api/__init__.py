from nsweb.core import app
from flask import Blueprint, render_template, jsonify
from flask_swagger import swagger


bp = Blueprint('api', __name__, url_prefix='/api/')


@bp.route('/')
def index():
    return render_template('home/api.html')


@bp.route('/swagger.json')
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Neurosynth API"
    return jsonify(swag)
