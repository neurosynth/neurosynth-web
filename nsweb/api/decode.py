from flask import jsonify, request, Blueprint, abort, send_file
from nsweb.api.schemas import DecodingSchema
from nsweb.models.decodings import Decoding, DecodingSet
from nsweb.core import cache, db
from nsweb.models.images import Image
from nsweb.initializers import settings
from nsweb import tasks
from .utils import send_nifti
import json
import re
import uuid
import requests
from os.path import join, basename, exists
import os
from datetime import datetime
from email.utils import parsedate
from nsweb.controllers import error_page
import pandas as pd
from .utils import make_cache_key


bp = Blueprint('api_decode', __name__, url_prefix='/api/decode')


@bp.route('/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_decoding():
    """
    Retrieve decoding data for a single image
    ---
    tags:
        - decode
    responses:
        200:
            description: Decoding data
        default:
            description: Decoding not found
    parameters:
        - in: query
          name: uuid
          description: UUID of the decoding
          required: false
          type: string
        - in: query
          name: image
          description: ID of image to decode
          type: integer
          required: false
        - in: query
          name: neurovault
          description: NeuroVault ID of image to decode
          type: integer
          required: false
        - in: query
          name: url
          description: URL of Nifti image to decode
          type: string
          required: false
    """
    dec = _get_decoding_object()
    schema = DecodingSchema()
    return jsonify(data=schema.dump(dec).data)


def _get_decoding_object(filter_display=True):

    dec = None

    if 'uuid' in request.args:
        dec = dec.filter_by(uuid=request.args['uuid']).first()

    elif 'image' in request.args:
        dec = decode_analysis_image(request.args['image'])

    elif 'neurovault' in request.args:
        dec = decode_neurovault(request.args['neurovault'])

    elif 'url' in request.args:
        dec = decode_url(request.args['url'])

    # Make sure we don't return non-displayable images
    if filter_display and dec is not None and not dec.display:
        dec = None

    return dec


@cache.memoize(timeout=3600)
def get_voxel_data(x, y, z, reference='terms', get_json=True, get_pp=True):
    """ Return the value at the specified voxel for all images in the named
    DecodingSet. x, y, z are MNI coordinates.
    Args:
        x, y, z (int): x, y, z coordinates
        reference (str): the name of the reference memmapped image set to use
        get_json (bool): when True, returns jsonized data. when False, returns
            a pandas Series or DataFrame.
        get_pp (bool): if True, returns posterior probabilities too (in
            addition to reverse inference z-scores).
    """
    # Make sure users don't request illegal sets
    valid_references = ['terms', 'topics']
    if reference not in valid_references:
        reference = valid_references[0]
    result = tasks.get_voxel_data.delay(
        reference, x, y, z, get_pp).wait()
    return result if get_json else pd.read_json(result)


def _get_decoding(**kwargs):
    """ Check if a Decoding matching the passed criteria already exists. """
    name = request.args.get('set', 'terms_20k')
    return Decoding.query.filter_by(**kwargs).join(DecodingSet) \
        .filter(DecodingSet.name == name).first()


def _run_decoder(**kwargs):

    kwargs['uuid'] = kwargs.get('uuid', uuid.uuid4().hex)
    # Default to reduced term reference set. Also allow
    # 'terms' or 'topics' shorthand.
    ds_name = request.args.get('set', 'terms_20k')
    if ds_name in ['terms', 'topics']:
        ds_name += '_20k'
    reference = DecodingSet.query.filter_by(name=ds_name).first()
    dec = Decoding(display=True, download=False, ip=request.remote_addr,
                   decoding_set=reference, **kwargs)

    # run decoder and wait for it to terminate
    result = tasks.decode_image.delay(dec.filename, reference.name,
                                      dec.uuid).wait()

    if result:
        dec.image_decoded_at = datetime.utcnow()
        db.session.add(dec)
        db.session.commit()

    return dec


@bp.route('/<string:uuid>/data/')
def get_data(uuid):
    dec = Decoding.query.filter_by(uuid=uuid).first()
    if dec is None:
        abort(404)
    data = open(join(settings.DECODING_RESULTS_DIR,
                     dec.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [{'analysis': f, 'r': round(float(v), 3)}
            for (f, v) in data if v.strip()]
    return jsonify(data=data)


@bp.route('/<string:uuid>/image/')
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
@bp.route('/<string:uuid>/scatter/<string:analysis>/')
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


# @bp.route('/data/')
# def get_data_api():
#     if 'url' in request.args:
#         id = decode_url(request.args['url'])
#     elif 'neurovault' in request.args:
#         id = decode_neurovault(request.args['neurovault'])
#     return get_data(id)


def decode_url(url, metadata={}):

    # Basic URL validation
    if not re.search('^https?\:\/\/', url):
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
            int(headers['content-length']) > 4000000:
        return error_page("The requested Nifti image is too large. Files must "
                          "be under 4 MB in size.")

    dec = _get_decoding(url=url)

    # Delete old record
    if not settings.CACHE_DECODINGS and dec is not None:
        db.session.delete(dec)
        db.session.commit()
        dec = None

    if dec is None:

        unique_id = uuid.uuid4().hex
        filename = join(settings.DECODED_IMAGE_DIR, unique_id + ext.group(0))

        f = requests.get(url)
        with open(filename, 'wb') as outfile:
            outfile.write(f.content)
        # Make sure celery worker has permission to overwrite
        os.chmod(filename, 0o666)

        # Named args to pass to Decoding initializer
        modified = headers.get('last-modified', None)
        if modified is not None:
            modified = datetime(*parsedate(modified)[:6])
        kwargs = {
            'uuid': unique_id,
            'url': url,
            'name': metadata.get('name', basename(url)),
            'image_modified_at': modified,
            'filename': filename,
            'neurovault_id': metadata.get('nv_id', None)
        }

        dec = _run_decoder(**kwargs)

    return dec

    # if render:
    #     return show(dec, dec.uuid)
    # else:
    #     return dec.uuid


def decode_neurovault(id):
    resp = requests.get('http://neurovault.org/api/images/%s/?format=json'
                        % str(id))
    metadata = json.loads(resp.content)
    if 'file' not in metadata:
        # return render_template('decode/missing.html')
        return None
    metadata['nv_id'] = id
    return decode_url(metadata['file'], metadata)


def decode_analysis_image(image):

    image = int(image)

    dec = _get_decoding(image_id=image)

    # Delete old record
    if not settings.CACHE_DECODINGS and dec is not None:
        db.session.delete(dec)
        db.session.commit()
        dec = None

    if dec is None:

        image = Image.query.get(image)
        filename = image.image_file

        kwargs = {
            'name': image.name,
            'filename': filename,
            'image_id': image.id
        }

        dec = _run_decoder(**kwargs)

    return dec
