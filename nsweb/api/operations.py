from nsweb.api import bp
from flask import jsonify, request
from nsweb.api.schemas import GeneSchema
from nsweb.models.genes import Gene
from nsweb.core import cache
import re


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string.decode('utf-8')


@bp.route('/genes/')
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
