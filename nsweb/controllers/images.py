from flask import send_from_directory, Blueprint, abort, request, jsonify, redirect, url_for, send_file
from nsweb.models import Image, Analysis, Location, Download
from nsweb.initializers import settings
from nsweb.initializers.settings import IMAGE_DIR
from nsweb.core import add_blueprint, db
from nsweb.models.decodings import Decoding, DecodingSet
import os
import datetime as dt
import re

bp = Blueprint('images',__name__,url_prefix='/images')

def send_nifti(filename, attachment_filename=None):
    """ Sends back a cache-controlled nifti image to the browser """
    if not os.path.exists(filename) or '..' in filename or '.nii' not in filename:
        abort(404)

    if attachment_filename is None:
        attachment_filename = os.path.basename(filename)

    resp = send_file(os.path.join(IMAGE_DIR, filename), as_attachment=True,
            attachment_filename=attachment_filename, conditional=True,
            add_etags=True)
    resp.last_modified = dt.datetime.fromtimestamp(os.path.getmtime(filename))
    resp.make_conditional(request)
    return resp

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
def get_decoding_data(image, reference='term'):

    # Fix this ugly-ass query...
    dec = db.session.query(Decoding)\
        .filter(Decoding.decoding_set_id == DecodingSet.id,
                DecodingSet.name == reference,
                Decoding.image_id == int(image)).first()

    if dec is None:
        abort(404)
    data = open(os.path.join(settings.DECODING_RESULTS_DIR,
                             dec.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [{reference: f, 'r': round(float(v), 3)} for (f, v) in data]
    return jsonify(data=data)


@bp.route('/anatomical')
def anatomical_underlay():
    return send_nifti(os.path.join(IMAGE_DIR, 'anatomical.nii.gz'),
                      'anatomical.nii.gz')

add_blueprint(bp)
