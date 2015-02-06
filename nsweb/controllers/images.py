from flask import Blueprint, abort, request, jsonify
from nsweb.models.images import Image
from nsweb.models.downloads import Download
from nsweb.initializers import settings
from nsweb.initializers.settings import IMAGE_DIR
from nsweb.core import add_blueprint, db
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
def get_decoding_data(image):

    dec = decode_analysis_image(image)
    # # Fix this ugly-ass query...
    # dec = db.session.query(Decoding)\
    #     .filter(Decoding.decoding_set_id == DecodingSet.id,
    #             DecodingSet.name == reference,
    #             Decoding.image_id == int(image)).first()

    if dec is None:
        abort(404)
    data = open(os.path.join(settings.DECODING_RESULTS_DIR,
                             dec.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    # data = [{'term': f, 'r': round(float(v), 3)} for (f, v) in data]
    data = [[f, round(float(v), 3)] for (f, v) in data]
    return jsonify(data=data)


@bp.route('/anatomical')
def anatomical_underlay():
    return send_nifti(os.path.join(IMAGE_DIR, 'anatomical.nii.gz'),
                      'anatomical.nii.gz')

add_blueprint(bp)
