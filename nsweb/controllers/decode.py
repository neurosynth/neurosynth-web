from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, send_file
from nsweb.models import Decoding
from nsweb.core import app, add_blueprint, db
from nsweb.initializers import settings
from nsweb.tasks import decode_image, make_scatterplot
from nsweb.controllers.images import send_nifti
from flask.helpers import url_for
import simplejson as json
from flask.ext.user import login_required, current_user
import re
import uuid
import requests
from os.path import join, basename, exists
import os
from datetime import datetime
from email.utils import parsedate

bp = Blueprint('decode',__name__,url_prefix='/decode')

@bp.route('/', methods=['GET'])
def index():

    # Decode from a URL or a NeuroVault ID
    if 'url' in request.args:
        return decode_from_url(request.args['url'])
    elif 'neurovault' in request.args:
        return decode_from_neurovault(request.args['neurovault'])

    return render_template('decode/index.html.slim')

def decode_from_url(url, metadata={}):

    # Basic URL validation
    if not url.startswith('http://'):
        url = 'http://' + url
    ext = re.search('\.nii(\.gz)?$', url)

    if ext is None:
        abort(404)  # Change to informative error message later

    # Check that an image exists at the URL
    head = requests.head(url)
    if head.status_code not in [200, 301, 302]: abort(404)
    headers = head.headers
    if 'content-length' in headers and int(headers['content-length']) > 2000000:
        abort(404)

    # Create record if it doesn't exist
    dec = Decoding.query.filter_by(url=url).first()

    # Determine whether to decode or not
    run_decoder = True if dec is None or not settings.CACHE_DECODINGS else False

    if dec is None:
        name = metadata.get('name', basename(url))
        neurovault_id = metadata.get('id', None)
        uid = uuid.uuid4().hex
        filename = join(settings.DECODED_IMAGE_DIR, uid + ext.group(0))
        modified = headers.get('last-modified', None)
        if modified is not None:
            modified = datetime(*parsedate(modified)[:6])


        dec = Decoding(url=url, neurovault_id=neurovault_id, filename=filename,
                uuid=uid, name=name, display=1, download=0, ip=request.remote_addr,
                image_modified_at=modified
                )
        dec.data = metadata

    if run_decoder:
        f = requests.get(url)
        with open(dec.filename, 'wb') as outfile:
            outfile.write(f.content)
        os.chmod(dec.filename, 0666)  # Make sure celery worker has permission to overwrite

        result = decode_image.delay(dec.filename).wait()  # wait for decoder to finish

        if result:
            dec.image_decoded_at = datetime.utcnow()
            db.session.add(dec)
            db.session.commit()        

    return show(dec, dec.uuid)


def decode_from_neurovault(id):

    if not re.match('\d+$', id): abort(404)
    resp = requests.get('http://neurovault.org/api/images/%s/?format=json' % str(id))
    metadata = json.loads(resp.content)
    return decode_from_url(metadata['file'], metadata)


@bp.route('/<string:uuid>/')
def show(decoding=None, uuid=None):
    if uuid is not None:
        decoding = Decoding.query.filter_by(uuid=uuid).first()

    if decoding is None: abort(404)

    images = [{
        'id': decoding.uuid,
        'name': decoding.name,
        'colorPalette': 'intense red-blue',
        'sign': 'both',
        'url': '/decode/%s/image' % decoding.uuid,
        'download': '/decode/%s/image' % decoding.uuid
    }]
    return render_template('decode/show.html.slim', decoding=decoding, images=json.dumps(images))


@bp.route('/<string:uuid>/data')
def get_data(uuid):
    dec = Decoding.query.filter_by(uuid=uuid).first()
    if dec is None: abort(404)
    data = open(join(settings.DECODING_RESULTS_DIR, dec.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [{'feature': f, 'r': round(float(v), 3)} for (f, v) in data]
    return jsonify(data=data)


@bp.route('/<string:uuid>/image')
def get_image(uuid):
    """ Return an uploaded image. These are handled separately from Neurosynth-generated
    images in order to prevent public access based on sequential IDs, as all access to 
    uploads must be via UUIDs. """
    dec = Decoding.query.filter_by(uuid=uuid).first()
    if dec is None: abort(404)
    return send_nifti(join(settings.DECODED_IMAGE_DIR, dec.filename), basename(dec.filename))


@bp.route('/<string:uuid>/scatter/<string:feature>.png')
@bp.route('/<string:uuid>/scatter/<string:feature>')
def get_scatter(uuid, feature):
    outfile = join(settings.DECODING_SCATTERPLOTS_DIR, uuid + '_' + feature + '.png')
    if not exists(outfile):
        """ Return .png of scatterplot between the uploaded image and specified feature. """
        dec = Decoding.query.filter_by(uuid=uuid).first()
        if dec is None: abort(404)
        result = make_scatterplot.delay(dec.filename, feature, dec.uuid, outfile=outfile, x_lab=dec.name).wait()
        if not exists(outfile): abort(404)
    return send_file(outfile, as_attachment=False, 
            attachment_filename=basename(outfile))


add_blueprint(bp)

