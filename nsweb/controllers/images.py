from flask import Blueprint, abort, request, jsonify
from nsweb.models.images import Image
from nsweb.models.downloads import Download
from nsweb.initializers import settings
from nsweb.initializers.settings import IMAGE_DIR
from nsweb.core import add_blueprint, db
from nsweb.controllers import error_page
from nsweb.controllers.decode import decode_analysis_image
from nsweb.controllers.helpers import send_nifti
import os

bp = Blueprint('images', __name__, url_prefix='/images')



@bp.route('/<int:val>/')
def download(val, fdr=True):
    image = Image.query.get_or_404(val)
    if not image.download:
        abort(404)
    # Log the download request
    db.session.add(Download(image_id=val, ip=request.remote_addr))
    db.session.commit()
    # Send the file
    filename = image.image_file if fdr else image.uncorrected_image_file
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

add_blueprint(bp)
