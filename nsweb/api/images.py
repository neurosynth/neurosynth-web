from flask import Blueprint, request, jsonify, abort
from nsweb.models.images import Image
from nsweb.models.downloads import Download
from .schemas import ImageSchema
from nsweb.core import cache
from .utils import make_cache_key
import re
from nsweb.core import db
from .utils import send_nifti
from nsweb.initializers import settings
from nsweb.initializers.settings import IMAGE_DIR
from nsweb.controllers import error_page
from nsweb.api.decode import decode_analysis_image
import os


bp = Blueprint('api_images', __name__, url_prefix='/api/images')


@bp.route('/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_images():
    """
    Retrieve image data
    ---
    tags:
        - images
    responses:
        200:
            description: Image data
        default:
            description: No images found
    parameters:
        - in: query
          name: limit
          description: Maximum number of images to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: search
          description: Search image fields (label, description)
          type: string
          required: false
        - in: query
          name: id
          description: PubMed ID(s) of one or more studies
          required: false
          collectionFormat: csv
          type: array
          items:
            type: integer
        - in: query
          name: type
          description: Associated object type
          type: string
          required: false
    """
    DEFAULT_LIMIT = 25
    MAX_LIMIT = 100
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    limit = min(limit, MAX_LIMIT)
    page = int(request.args.get('page', 1))

    images = Image.query.filter_by(display=1, download=1)

    if 'type' in request.args:
        images = images.filter_by(type=request.args['type'])

    if 'id' in request.args:
        ids = re.split('[\s,]+', request.args['id'].strip(' ,'))
        images = images.filter(Image.id.in_([int(x) for x in ids]))

    if 'search' in request.args and len(request.args['search']) > 1:
        search = '%{}%'.format(request.args['search'])
        images = images.filter(Image.label.like(search) |
                               Image.description.like(search))

    images = images.paginate(page, limit, False).items
    schema = ImageSchema(many=True)
    return jsonify(data=schema.dump(images).data)


@bp.route('/<int:val>')
def get_image(val, unthresholded=False):
    image = Image.query.get(val)
    if image is not None and image.display:
        data = ImageSchema().dump(image).data
    else:
        data = {}
    return jsonify(data=data)


@bp.route('/<int:val>/download')
@bp.route('/<int:val>/download.nii.gz')
def download(val, unthresholded=False):
    image = Image.query.get_or_404(val)
    if not image.download:
        abort(404)
    # Log the download request
    db.session.add(Download(image_id=val, ip=request.remote_addr))
    db.session.commit()
    # Send the file
    filename = image.image_file if not unthresholded \
        else image.uncorrected_image_file
    return send_nifti(filename)


@bp.route('/<int:image>/decode/')
def get_decoding_data(image, get_json=True):

    if Image.query.get(image) is None:
        return error_page("Invalid image requested for decoding. Please check"
                          " to make sure there is a valid image with id=%d." %
                          image)
    dec = decode_analysis_image(image)
    df = os.path.join(settings.DECODING_RESULTS_DIR, dec.uuid + '.txt')
    if not os.path.exists(df):
        return error_page("An unspecified error occurred during decoding.")
    data = open(df).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [[f, round(float(v or '0'), 3)] for (f, v) in data]
    return jsonify(data=data) if get_json else data


@bp.route('/anatomical')
def anatomical_underlay():
    return send_nifti(os.path.join(IMAGE_DIR, 'anatomical.nii.gz'),
                      'anatomical.nii.gz')
