from flask import (Blueprint, render_template, abort, send_file)
from nsweb.models.genes import Gene
from nsweb.core import add_blueprint
from nsweb.tasks import make_scatterplot
from nsweb.initializers import settings
from nsweb.controllers import error_page
from nsweb.controllers.decode import decode_analysis_image
import simplejson as json
from os.path import join, basename, exists

bp = Blueprint('genes', __name__, url_prefix='/genes')


@bp.route('/')
def index():
    return render_template('genes/index.html.slim')


@bp.route('/<string:name>/')
def show(name):
    gene = Gene.query.filter_by(symbol=name).first()
    if gene is None:
        return error_page("We have no data for the gene '%s'" % name)
    image = gene.images[0]
    # Run decoder if it hasn't been run before
    dec = decode_analysis_image(image.id)
    url = '/images/%s' % image.id
    images = [{
        'id': image.id,
        'name': name,
        'url':  url,
        'colorPalette': 'intense red-blue',
        'download': url,
        'sign': 'both'
    }]
    return render_template('genes/show.html.slim', gene=gene,
                           images=json.dumps(images), image_id=dec.uuid)


@bp.route('/<string:val>/scatter/<string:analysis>.png')
def get_scatter(val, analysis):
    outfile = join(
        settings.DECODING_SCATTERPLOTS_DIR, val + '_' + analysis + '.png')
    if not exists(outfile):
        """ Return .png of scatter plot between the uploaded image and
        specified analysis. """
        gene = Gene.query.filter_by(symbol=val).first()
        if gene is None:
            abort(404)
        make_scatterplot.delay(
            gene.images[0].image_file, analysis, gene.symbol,
            x_lab='%s expression level' % gene.symbol, outfile=outfile,
            gene_masks=True).wait()
    return send_file(outfile, as_attachment=False,
                     attachment_filename=basename(outfile))

add_blueprint(bp)
