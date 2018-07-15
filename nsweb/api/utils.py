from flask import send_file, abort, request
from nsweb.initializers.settings import IMAGE_DIR
import datetime as dt
import os


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string.decode('utf-8')


def send_nifti(filename, attachment_filename=None):
    """ Sends back a cache-controlled nifti image to the browser """
    if not os.path.exists(filename) or '..' in filename or \
            '.nii' not in filename:
        abort(404)

    if attachment_filename is None:
        attachment_filename = os.path.basename(filename)

    resp = send_file(os.path.join(IMAGE_DIR, filename), as_attachment=True,
                     attachment_filename=attachment_filename, conditional=True,
                     add_etags=True)
    resp.last_modified = dt.datetime.fromtimestamp(os.path.getmtime(filename))
    resp.make_conditional(request)
    return resp
