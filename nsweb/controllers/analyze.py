from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, send_file
from nsweb.models.analyses import Analysis, AnalysisImage
from nsweb.core import app, add_blueprint, db
from nsweb.initializers import settings
from nsweb.tasks import run_metaanalysis
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


bp = Blueprint('analyze',__name__,url_prefix='/analyze')

@bp.route('/', methods=['GET'])
def index():
    return render_template('analyze/index.html.slim')

@bp.route('/<id>/', methods=['GET', 'POST'])
def show(id):
    return render_template('analyze/show.html.slim')

@login_required
def run():

    if 'ids' not in request.args:
        abort(404)  # TODO: return sensible error message
    result = run_metaanalysis.delay(request.args['ids']).wait()

    if result:

        # Create the Analysis record
        uid = uuid.uuid4().hex
        name = request.args.get('name', None)
        description = request.args.get('description', None)
        analysis = Analysis(name=request.args['name'], description=description, 
            uuid=uid, ip=request.remote_addr, user=current_user)

        # Add images
        image_dir = join(settings.IMAGE_DIR, 'analyses')
        analysis.images = [
            AnalysisImage(image_file=join(image_dir, name + '_pAgF_z_FDR_0.01.nii.gz'),
                label='%s: forward inference' % name,
                stat='z-score',
                display=1,
                download=1),
            AnalysisImage(image_file=join(image_dir, name + '_pFgA_z_FDR_0.01.nii.gz'),
                label='%s: reverse inference' % name,
                stat='z-score',
                display=1,
                download=1)
        ]

        db.session.add(analysis)
        db.session.commit()

        # Add studies
        for s in ids:
            db.session.add(Inclusion(analysis=analysis, study_id=int(s)))
            db.session.commit()

@bp.route('/<id>/images')
### TODO: move image retrieval from multiple controllers into a separate helper
def get_images(id):
    analysis = Analysis.query.filter_by(uuid=id).first()
    if analysis is None:
        abort(404)
    images = [{
        'id': img.id,
        'name': img.label,
        'colorPalette': 'red' if 'reverse' in img.label else 'blue',
        # "intent": (img.stat + ':').capitalize(),
        'url': '/images/%s' % img.id,
        'visible': 1 if 'reverse' in img.label else 0,
        'download': '/images/%s' % img.id,
        'intent': 'z-score'
    } for img in analysis.images if img.display]
    return jsonify(data=images)

@bp.route('<id>/studies')
def get_studies(id):
    analysis = Analysis.query.filter_by(uuid=id).first()
    if analysis is None:
        abort(404)
    pass

