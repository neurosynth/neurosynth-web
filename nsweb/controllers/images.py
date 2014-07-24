from flask import send_from_directory, Blueprint, abort, request, jsonify, redirect, url_for, send_file
from nsweb.models import Image, Feature, Location
from nsweb.initializers.settings import IMAGE_DIR
from nsweb.core import add_blueprint
import os
import datetime as dt

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
def download(val):
    image = Image.query.get_or_404(val)
    if not image.download:
        abort(404)
    return send_nifti(image.image_file)

@bp.route('/anatomical')
def anatomical_underlay():
    return send_nifti(os.path.join(IMAGE_DIR, 'anatomical.nii.gz'), 'anatomical.nii.gz')

add_blueprint(bp)