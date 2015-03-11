from nsweb.core import add_blueprint, app
from flask import Blueprint, render_template
from flask_swagger import swagger

bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

from nsweb.api.operations import *

add_blueprint(bp)


@bp.route('/')
def index():
    return render_template('home/api.html.slim')


@bp.route('/swagger.json')
def spec():
    swag = swagger(app)
    swag['info'] = {
        'version': "1.0",
        'title': "Neurosynth API v2",
        'description': " Documentation and interface to the "
        "Neurosynth API (v2).",
        'contact': {
            "name": "Neurosynth API support",
            "url": "https://github.com/neurosynth/neurosynth-web/issues"
        }
    }
    swag['definitions'] = {
        'Analysis': {
            'type': 'object',
            'required': ['id', 'name'],
            'properties': {
                'studies': {
                    'type': 'array',
                    'items': {'type': 'integer'}
                },
                'images': {
                    'type': 'array',
                    'items': {'type': 'integer'}
                },
                'n_studies': {'type': 'integer'},
                'n_activations': {'type': 'integer'},
                'type': {'type': 'string'},
                'name': {'type': 'string'},
                'id': {'type': 'integer'},
                'description': {'type': 'string'}
            }
        },
        'Location': {
            'type': 'object',
            'required': ['x', 'y', 'z'],
            'properties': {
                'x': {
                    'description': 'x-axis coordinate',
                    'type': 'integer'
                },
                'y': {
                    'description': 'y-axis coordinate',
                    'type': 'integer'
                },
                'z': {
                    'description': 'z-axis coordinate',
                    'type': 'integer'
                },
                'r': {
                    'description': 'radius of activation search sphere',
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 20,
                    'default': 6
                }
            }
        }
    }
    return jsonify(swag)
