from flask import jsonify, request, Blueprint, abort, send_file, url_for
from .utils import make_cache_key
from nsweb.api.schemas import GeneSchema
from nsweb.models.genes import Gene
from nsweb.core import cache
import re
from os.path import exists, join, basename
from nsweb.tasks import make_scatterplot
from nsweb.initializers import settings


bp = Blueprint('api_genes', __name__, url_prefix='/api/genes')


@bp.route('/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_genes():
    """
    Retrieve gene data
    ---
    tags:
        - genes
    responses:
        200:
            description: Gene information
        default:
            description: No genes found
    parameters:
        - in: query
          name: limit
          description: Maximum number of genes to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: symbol
          description: Gene symbol
          type: array
          required: false
          collectionFormat: csv
          items:
            type: string
        - in: query
          name: id
          description: Gene ID(s)
          required: false
          collectionFormat: csv
          type: array
          items:
            type: integer
    """
    DEFAULT_LIMIT = 25
    MAX_LIMIT = 100
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    limit = min(limit, MAX_LIMIT)
    page = int(request.args.get('page', 1))

    genes = Gene.query

    if 'id' in request.args:
        ids = re.split('[\s,]+', request.args['id'].strip(' ,'))
        genes = genes.filter(Gene.id.in_([int(x) for x in ids]))

    if 'symbol' in request.args:
        symbols = re.split('[\s,]+', request.args['symbol'].strip(' ,'))
        genes = genes.filter(Gene.symbol.in_(symbols))

    genes = genes.paginate(page, limit, False).items
    schema = GeneSchema(many=True)
    return jsonify(data=schema.dump(genes).data)


@bp.route('/dt/')
def datatable_genes():

    results_per_page = int(request.args['length'])
    offset = int(request.args['start'])

    order_by = '{0} {1}'.format(
        ['symbol', 'name', 'synonyms', 'locus_type']
        [int(request.args['order[0][column]'])],
        str(request.args['order[0][dir]']))
    search = str(request.args['search[value]']).strip()

    data = Gene.query
    if search:
        search = '%{}%'.format(search)
        data = data.filter(Gene.name.like(search) |
                           Gene.symbol.like(search) |
                           Gene.synonyms.like(search))
    data = data.order_by(order_by)
    data = data.paginate(page=(offset / results_per_page) + 1,
                         per_page=results_per_page, error_out=False)
    result = {}
    result['draw'] = int(request.args['draw'])  # for security
    result['recordsTotal'] = Gene.query.count()
    result['recordsFiltered'] = data.total
    result['data'] = [
        ['<a href={0}>{1}</a>'.format(
            url_for('genes.show', symbol=d.symbol), d.symbol),
         d.name,
         d.synonyms,
         d.locus_type
         ] for d in data.items]
    return jsonify(**result)


@bp.route('/<string:val>/scatter/<string:analysis>.png')
def get_scatter(val, analysis):
    outfile = join(settings.DECODING_SCATTERPLOTS_DIR,
                   val + '_' + analysis + '.png')
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
