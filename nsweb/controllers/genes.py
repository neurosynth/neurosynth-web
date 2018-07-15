from flask import Blueprint, render_template, url_for
from nsweb.models.genes import Gene
from nsweb.controllers import error_page
from nsweb.api.decode import decode_analysis_image
import json


bp = Blueprint('genes', __name__, url_prefix='/genes')


@bp.route('/')
def index():
    return render_template('genes/index.html')


@bp.route('/<string:symbol>/')
def show(symbol):
    gene = Gene.query.filter_by(symbol=symbol).first()
    if gene is None:
        return error_page("We have no data for the gene '%s'" % symbol)
    image = gene.images[0]
    # Run decoder if it hasn't been run before
    dec = decode_analysis_image(image.id)
    url = url_for('api_images.download', val=image.id)
    images = [{
        'id': image.id,
        'name': symbol,
        'url':  url,
        'colorPalette': 'intense red-blue',
        'download': url,
        'sign': 'both'
    }]
    return render_template('genes/show.html', gene=gene,
                           images=json.dumps(images), image_id=dec.uuid)
