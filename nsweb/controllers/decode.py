from flask import (Blueprint, render_template, request, abort, send_file,
                   jsonify)
from nsweb.models.decodings import Decoding, DecodingSet
from nsweb.models.images import Image
from nsweb.core import add_blueprint, db, cache
from nsweb.initializers import settings
from nsweb import tasks
from nsweb.controllers.helpers import send_nifti
import simplejson as json
import re
import uuid
import requests
from os.path import join, basename, exists
import os
from datetime import datetime
from email.utils import parsedate
from nsweb.controllers import error_page

bp = Blueprint('decode', __name__, url_prefix='/decode')


@bp.route('/', methods=['GET'])
def index():

    # Decode from a URL or a NeuroVault ID
    if 'url' in request.args:
        return decode_url(request.args['url'])
    elif 'neurovault' in request.args:
        return decode_neurovault(request.args['neurovault'])
    elif 'image' in request.args:
        return decode_analysis_image(request.args['image'])

    return render_template('decode/index.html.slim')


@cache.memoize(timeout=3600)
def get_voxel_data(x, y, z, reference='terms_full', get_json=True):
    """ Return the value at the specified voxel for all images in the named
    DecodingSet. x, y, z are MNI coordinates. """
    # Make sure users don't request illegal sets
    valid_references = ['terms_full', 'topics_full']
    if reference not in valid_references:
        reference = valid_references[0]
    reference = DecodingSet.query.filter_by(name=reference).first()
    ref = {
        'name': reference.name,
        'n_voxels': reference.n_voxels,
        'n_images': reference.n_images,
        'is_subsampled': reference.is_subsampled
    }
    result = tasks.get_voxel_data.delay(ref, x, y, z).wait()
    return result.to_json() if get_json else result


def _get_decoding(**kwargs):
    """ Check if a Decoding matching the passed criteria already exists. """
    name = request.args.get('set', 'terms_20k')
    return Decoding.query.filter_by(**kwargs).join(DecodingSet) \
        .filter(DecodingSet.name == name).first()


def _run_decoder(**kwargs):

    kwargs['uuid'] = kwargs.get('uuid', uuid.uuid4().hex)
    ds_name = request.args.get('set', 'terms_20k')
    reference = DecodingSet.query.filter_by(name=ds_name).first()
    dec = Decoding(display=1, download=0, ip=request.remote_addr,
                   decoding_set=reference, **kwargs)

    # Call the decoder in the background. We can't easily pass our own
    # classes to celery, so pass a dict with relevant DecodingSet info.
    ref = {
        'name': reference.name,
        'n_voxels': reference.n_voxels,
        'n_images': reference.n_images,
        'is_subsampled': reference.is_subsampled
    }

    # run decoder and wait for it to terminate
    result = tasks.decode_image.delay(dec.filename, ref, dec.uuid).wait()

    if result:
        dec.image_decoded_at = datetime.utcnow()
        db.session.add(dec)
        db.session.commit()

    return dec


def decode_analysis_image(image):

    image = int(image)

    dec = _get_decoding(image_id=image)

    if dec is None or not settings.CACHE_DECODINGS:

        image = Image.query.get(image)
        filename = image.image_file

        kwargs = {
            'name': image.name,
            'filename': filename,
            'image_id': image.id
        }

        dec = _run_decoder(**kwargs)

    return dec


def decode_url(url, metadata={}, render=True):

    # Basic URL validation
    if not url.startswith('http://'):
        url = 'http://' + url
    ext = re.search('\.nii(\.gz)?$', url)

    if ext is None:
        return error_page("Invalid image extension; currently the decoder only"
                          " accepts images in nifti format.")

    # Check that an image exists at the URL
    head = requests.head(url)
    if head.status_code not in [200, 301, 302]:
        return error_page("No image was found at the provided URL.")
    headers = head.headers
    if 'content-length' in headers and \
            int(headers['content-length']) > 4000000 and render:
        return error_page("The requested Nifti image is too large. Files must "
                          "be under 4 MB in size.")

    dec = _get_decoding(url=url)

    if dec is None or not settings.CACHE_DECODINGS:

        unique_id = uuid.uuid4().hex
        filename = join(settings.DECODED_IMAGE_DIR, unique_id + ext.group(0))

        f = requests.get(url)
        with open(filename, 'wb') as outfile:
            outfile.write(f.content)
        # Make sure celery worker has permission to overwrite
        os.chmod(filename, 0666)

        # Named args to pass to Decoding initializer
        modified = headers.get('last-modified', None)
        if modified is not None:
            modified = datetime(*parsedate(modified)[:6])
        kwargs = {
            'uuid': unique_id,
            'url': url,
            'name': metadata.get('name', basename(url)),
            'image_modified_at': modified,
            'filename': filename
        }

        dec = _run_decoder(**kwargs)

        dec.data = metadata
        db.session.add(dec)
        db.session.commit()

    if render:
        return show(dec, dec.uuid)
    else:
        return dec.uuid


def decode_neurovault(id, render=True):
    resp = requests.get('http://neurovault.org/api/images/%s/?format=json'
                        % str(id))
    metadata = json.loads(resp.content)
    if 'file' not in metadata:
        return render_template('decode/missing.html.slim')
    return decode_url(metadata['file'], metadata, render=render)


@bp.route('/<string:uuid>/')
def show(decoding=None, uuid=None):
    if uuid is not None:
        decoding = Decoding.query.filter_by(uuid=uuid).first()

    if decoding is None:
        abort(404)

    images = [{
        'id': decoding.uuid,
        'name': decoding.name,
        'colorPalette': 'intense red-blue',
        'sign': 'both',
        'url': '/decode/%s/image' % decoding.uuid,
        'download': '/decode/%s/image' % decoding.uuid
    }]
    return render_template('decode/show.html.slim', image_id=decoding.uuid,
                           images=json.dumps(images))


@bp.route('/<string:uuid>/data')
def get_data(uuid):
    dec = Decoding.query.filter_by(uuid=uuid).first()
    if dec is None:
        abort(404)
    data = open(join(settings.DECODING_RESULTS_DIR,
                     dec.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [{'analysis': f, 'r': round(float(v), 3)} for (f, v) in data]
    return jsonify(data=data)


@bp.route('/<string:uuid>/image')
def get_image(uuid):
    """ Return an uploaded image. These are handled separately from
    Neurosynth-generated images in order to prevent public access based on
    sequential IDs, as all access to uploads must be via UUIDs. """
    dec = Decoding.query.filter_by(uuid=uuid).first()
    if dec is None:
        abort(404)
    return send_nifti(join(settings.DECODED_IMAGE_DIR, dec.filename),
                      basename(dec.filename))


@bp.route('/<string:uuid>/scatter/<string:analysis>.png')
@bp.route('/<string:uuid>/scatter/<string:analysis>')
def get_scatter(uuid, analysis):
    outfile = join(settings.DECODING_SCATTERPLOTS_DIR,
                   uuid + '_' + analysis + '.png')
    if not exists(outfile):
        """ Return .png of scatterplot between the uploaded image and specified
        analysis. """
        dec = Decoding.query.filter_by(uuid=uuid).first()
        if dec is None:
            abort(404)
        result = tasks.make_scatterplot.delay(
            dec.filename, analysis, dec.uuid, outfile=outfile,
            x_lab=dec.name).wait()
        if not exists(outfile):
            abort(404)
    return send_file(
        outfile, as_attachment=False, attachment_filename=basename(outfile))

### API ROUTES ###


@bp.route('/data/')
def get_data_api():
    if 'url' in request.args:
        id = decode_url(request.args['url'], render=False)
    elif 'neurovault' in request.args:
        id = decode_neurovault(request.args['neurovault'], render=False)
    return get_data(id)

add_blueprint(bp)
