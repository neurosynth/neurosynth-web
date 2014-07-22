from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, send_file
from nsweb.models import Upload
from nsweb.core import app, add_blueprint, db
from nsweb.initializers import settings
from nsweb.tasks import decode_image, make_scatterplot
from flask.helpers import url_for
import simplejson as json
from flask.ext.uploads import UploadSet, configure_uploads
from flask.ext.user import login_required, current_user
from nsweb.forms.upload import UploadForm
import re
import uuid
from os.path import join, basename, exists

bp = Blueprint('decode',__name__,url_prefix='/decode')

# Configure image uploads--hould probably move out of here and into core.py
app.config['UPLOADED_IMAGES_DEST'] = settings.IMAGE_UPLOAD_DIR
images = UploadSet('images', ('gz', 'nii'))
configure_uploads(app, (images))


@bp.route('/', methods=['GET','POST'])
@login_required
def index():
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

@bp.route('/<string:val>/')
@login_required
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
@login_required
def get_data(val):
    u = Upload.query.filter_by(uuid=val).first()
    if u is None: abort(404)
    data = open(join(settings.DECODING_RESULTS_DIR, u.uuid + '.txt')).read().splitlines()
    data = [x.split('\t') for x in data]
    data = [{'feature': f, 'r': round(float(v), 3)} for (f, v) in data]
    return jsonify(data=data)

@bp.route('/<string:val>/image')
@login_required
def get_image(val):
    """ Return an uploaded image. These are handled separately from Neurosynth-generated
    images in order to prevent public access based on sequential IDs, as all access to 
    uploads must be via UUIDs. """
    u = Upload.query.filter_by(uuid=val).first()
    if u is None: abort(404)
    return send_file(join(settings.IMAGE_UPLOAD_DIR, u.image_file), as_attachment=True, 
            attachment_filename=basename(u.image_file))

@bp.route('/<string:val>/scatter/<string:feature>.png')
@login_required
def get_scatter(val, feature):
    outfile = join(settings.DECODING_SCATTERPLOTS_DIR, val + '_' + feature + '.png')
    print outfile
    if not exists(outfile):
        """ Return .png of scatterplot between the uploaded image and specified feature. """
        u = Upload.query.filter_by(uuid=val).first()
        if u is None: abort(404)
        print "Decoding..."
        result = make_scatterplot.delay(u.image_file, feature, u.uuid, outfile=outfile).wait()
    return send_file(outfile, as_attachment=False, 
            attachment_filename=basename(outfile))

add_blueprint(bp)