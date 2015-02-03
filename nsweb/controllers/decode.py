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
from nsweb.controllers import error_page

bp = Blueprint('decode',__name__,url_prefix='/decode')

@bp.route('/', methods=['GET'])
def index():

    # Decode from a URL or a NeuroVault ID
    if 'url' in request.args:
        return decode_from_url(request.args['url'])
    elif 'neurovault' in request.args:
        return decode_from_neurovault(request.args['neurovault'])

    return render_template('decode/index.html.slim')

def decode_from_url(url, metadata={}, render=True):

    # Basic URL validation
    if not url.startswith('http://'):
        url = 'http://' + url
    ext = re.search('\.nii(\.gz)?$', url)

    if ext is None:
        return error_page("Invalid image extension; currently the decoder only accepts images in nifti format.")

    # Check that an image exists at the URL
    head = requests.head(url)
    if head.status_code not in [200, 301, 302]:
        return error_page("No image was found at the provided URL.")
    headers = head.headers
    if 'content-length' in headers and int(headers['content-length']) > 4000000 and render:
        return error_page("The requested Nifti image is too large. Files must be under 4 MB in size.")

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

    if render:
        return show(dec, dec.uuid)
    else:
        return dec.uuid


def decode_from_neurovault(id, render=True):

    if not re.match('\d+$', id):
        error_page("Invalid NeuroVault ID!")
    resp = requests.get('http://neurovault.org/api/images/%s/?format=json' % str(id))
    metadata = json.loads(resp.content)
    return decode_from_url(metadata['file'], metadata, render=render)


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
    data = [{'analysis': f, 'r': round(float(v), 3)} for (f, v) in data]
    return jsonify(data=data)


@bp.route('/<string:uuid>/image')
def get_image(uuid):
    """ Return an uploaded image. These are handled separately from Neurosynth-generated
    images in order to prevent public access based on sequential IDs, as all access to 
    uploads must be via UUIDs. """
    dec = Decoding.query.filter_by(uuid=uuid).first()
    if dec is None: abort(404)
    return send_nifti(join(settings.DECODED_IMAGE_DIR, dec.filename), basename(dec.filename))


@bp.route('/<string:uuid>/scatter/<string:analysis>.png')
@bp.route('/<string:uuid>/scatter/<string:analysis>')
def get_scatter(uuid, analysis):
    outfile = join(settings.DECODING_SCATTERPLOTS_DIR, uuid + '_' + analysis + '.png')
    if not exists(outfile):
        """ Return .png of scatterplot between the uploaded image and specified analysis. """
        dec = Decoding.query.filter_by(uuid=uuid).first()
        if dec is None: abort(404)
        result = make_scatterplot.delay(dec.filename, analysis, dec.uuid, outfile=outfile, x_lab=dec.name).wait()
        if not exists(outfile): abort(404)
    return send_file(outfile, as_attachment=False, 
            attachment_filename=basename(outfile))

### API ROUTES ###
@bp.route('/data/')
def get_data_api():
    if 'url' in request.args:
        id = decode_from_url(request.args['url'], render=False)
    elif 'neurovault' in request.args:
        id = decode_from_neurovault(request.args['neurovault'], render=False)
    return get_data(id)

add_blueprint(bp)

