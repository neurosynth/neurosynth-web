from flask import Blueprint, render_template, abort, url_for, request
from nsweb.api.decode import _get_decoding_object
from nsweb.models.decodings import Decoding
import json
from nsweb.controllers import error_page


bp = Blueprint('decode', __name__, url_prefix='/decode')


@bp.route('/', methods=['GET'])
def index():
    # Call API to do the decoding
    status, dec = _get_decoding_object()

    if status == 200:
        return show(dec, dec.uuid)

    elif status == 99:
        return render_template('decode/index.html')

    else:
        return error_page(dec)


@bp.route('/<string:uuid>/')
def show(decoding=None, uuid=None):
    if uuid is not None:
        decoding = Decoding.query.filter_by(uuid=uuid).first()

    if decoding is None:
        abort(404)

    file_loc = url_for('api_decode.get_image', uuid=decoding.uuid)

    images = [{
        'id': decoding.uuid,
        'name': decoding.name,
        'colorPalette': 'intense red-blue',
        'sign': 'both',
        'url': file_loc,
        'download': file_loc
    }]
    return render_template('decode/show.html', image_id=decoding.uuid,
                           images=json.dumps(images),
                           decoding=decoding)
