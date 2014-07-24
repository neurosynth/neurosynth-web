from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, send_file
from nsweb.models import Upload
from nsweb.core import app, add_blueprint, db
from nsweb.initializers import settings
from nsweb.tasks import decode_image, make_scatterplot
from nsweb.controllers.images import send_nifti
from flask.helpers import url_for
import simplejson as json
from flask.ext.uploads import UploadSet, configure_uploads
from flask.ext.user import login_required, current_user
from nsweb.forms.upload import UploadForm
import re
import uuid
import requests
from os.path import join, basename, exists

bp = Blueprint('decode',__name__,url_prefix='/decode')

# Configure image uploads--hould probably move out of here and into core.py
app.config['UPLOADED_IMAGES_DEST'] = settings.IMAGE_UPLOAD_DIR
images = UploadSet('images', ('gz', 'nii'))
configure_uploads(app, (images))


@bp.route('/', methods=['GET','POST'])
@login_required
def index():
    
    if 'url' in request.args:
        print "HI"
        return decode_from_url(request.args['url'])

    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        uid = uuid.uuid4().hex
        ext = re.search('\.nii(\.gz)?$', request.files['image_file'].filename).group(0)
        filename = images.save(request.files['image_file'], name=uid + ext)
        # img = Upload(image_file=filename, user=current_user, uuid=uid, ip=request.remote_addr, display=1, download=0)
        img = Upload(image_file=filename, user=current_user, uuid=uid, display=1, download=0)
        db.session.add(img)
        db.session.commit()
        result = decode_image.delay(img.image_file).wait()  # wait for decoder to finish
        return redirect(url_for('decode.show', val=img.uuid))       
    return render_template('decode/index.html.slim', form=form)

def decode_from_url(url):
    if not url.startswith('http://'):
        url = 'http://' + url
    ext = re.search('\.nii(\.gz)?$', url)
    if ext is None:
        abort(404)  # Change to informative error message later
    head = requests.head(url).headers
    if 'content-length' in head and int(head['content-length']) > 2000000:
        abort(404)
    f = requests.get(url)
    uid = uuid.uuid4().hex
    filename = join(settings.IMAGE_UPLOAD_DIR, uid + ext.group(0))
    open(filename, 'wb').write(f.content)
    img = Upload(image_file=filename, label=url, user=None, uuid=uid, display=1, download=0)
    db.session.add(img)
    db.session.commit()
    result = decode_image.delay(filename).wait()  # wait for decoder to finish
    return redirect(url_for('decode.show', val=img.uuid))

@bp.route('/<string:val>/')
def show(val):
    u = Upload.query.filter_by(uuid=val).first()
    if u is None: abort(404)
    images = [{
        'id': u.uuid,
        'name': 'Uploaded image',
        'colorPalette': 'red-yellow-blue',
        'url': '/decode/%s/image' % u.uuid,
    }]
    return render_template('decode/show.html.slim', id=u.uuid, images=json.dumps(images))

@bp.route('/<string:val>/data')
def get_data(val):
    u = Upload.query.filter_by(uuid=val).first()
    if u is None: abort(404)
    data = open(join(settings.DECODING_RESULTS_DIR, u.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [{'feature': f, 'r': round(float(v), 3)} for (f, v) in data]
    return jsonify(data=data)

@bp.route('/<string:val>/image')
def get_image(val):
    """ Return an uploaded image. These are handled separately from Neurosynth-generated
    images in order to prevent public access based on sequential IDs, as all access to 
    uploads must be via UUIDs. """
    u = Upload.query.filter_by(uuid=val).first()
    if u is None: abort(404)
    return send_nifti(join(settings.IMAGE_UPLOAD_DIR, u.image_file), basename(u.image_file))

@bp.route('/<string:val>/scatter/<string:feature>.png')
@bp.route('/<string:val>/scatter/<string:feature>')
def get_scatter(val, feature):
    outfile = join(settings.DECODING_SCATTERPLOTS_DIR, val + '_' + feature + '.png')
    if not exists(outfile):
        """ Return .png of scatterplot between the uploaded image and specified feature. """
        u = Upload.query.filter_by(uuid=val).first()
        if u is None: abort(404)
        result = make_scatterplot.delay(u.image_file, feature, u.uuid, outfile=outfile).wait()
        if not exists(outfile): abort(404)
    return send_file(outfile, as_attachment=False, 
            attachment_filename=basename(outfile))

add_blueprint(bp)