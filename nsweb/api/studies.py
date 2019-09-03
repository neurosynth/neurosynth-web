import urllib
import re

from flask import jsonify, request, Blueprint, url_for
from sqlalchemy import asc, desc
# from flask_user import login_required

from .utils import make_cache_key
from nsweb.api.schemas import StudySchema
from nsweb.models.studies import Study
from nsweb.core import cache
from nsweb import tasks


bp = Blueprint('api_studies', __name__, url_prefix='/api/studies')


@bp.route('/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_studies():
    """
    Retrieve study data
    ---
    tags:
        - studies
    responses:
        200:
            description: Study data
        default:
            description: No studies found
    parameters:
        - in: query
          name: limit
          description: Maximum number of studies to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: search
          description: Search study fields (title, authors, journal, and year)
          type: string
          required: false
        - in: query
          name: pmid
          description: PubMed ID(s) of one or more studies
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

    studies = Study.query

    if 'pmid' in request.args or 'id' in request.args:
        ids = request.args.get('id', None)
        ids = request.args.get('pmid', ids)
        ids = re.split('[\s,]+', ids.strip(' ,'))
        studies = studies.filter(Study.pmid.in_([int(x) for x in ids]))

    if 'search' in request.args and len(request.args['search']) > 1:
        search = '%{}%'.format(request.args['search'])
        studies = studies.filter(Study.title.like(search) |
                                 Study.authors.like(search) |
                                 Study.journal.like(search) |
                                 Study.year.like(search))

    studies = studies.paginate(page, limit, False).items
    schema = StudySchema(many=True)
    return jsonify(data=schema.dump(studies).data)


@bp.route('/<int:val>/tables/')
def get_tables(val):
    study = Study.query.get_or_404(val)
    colors = ['blue', 'red', 'yellow', 'green', 'purple', 'brown']
    tables = {}
    for p in study.peaks:
        if p.table not in tables:
            tables[p.table] = {
                'name': 'table_' + str(p.table),
                'colorPalette': colors.pop(0),
                'data': {
                    'dims': [91, 109, 91],
                    'peaks': [],
                }
            }
        x, y, z = int(p.x), int(p.y), int(p.z)
        tables[p.table]['data']['peaks'].append({"x": x, "y": y, "z": z})
    return jsonify(data=list(tables.values()))


@bp.route('/dt/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_study_list():

    # if 'expression' in request.args:
    #     return get_studies_by_expression(request.args['expression'])

    data = Study.query

    val = str(request.args['search[value]']).strip()
    if val:
        str_val = '%{}%'.format(val)
        q = Study.title.ilike(str_val) | Study.authors.ilike(str_val) | \
            Study.journal.ilike(str_val)
        try:
            int_val = int(val)
            q = q | (Study.year == int_val) | (Study.pmid == int_val)
        except Exception as e:
            pass
        data = data.filter(q)

    # Sorting
    direction = str(request.args['order[0][dir]'])
    ord_col = ['title', 'authors', 'journal', 'year', 'pmid'][
        int(request.args['order[0][column]'])]
    dir_func = asc if direction == 'asc' else desc
    data = data.order_by(dir_func(ord_col))

    # Pagination
    results_per_page = int(request.args['length'])
    offset = int(request.args['start'])
    data = data.paginate(
        page=(offset / results_per_page) + 1, per_page=results_per_page,
        error_out=False)

    result = {}
    result['draw'] = int(request.args['draw'])  # for security
    result['recordsTotal'] = Study.query.count()
    result['recordsFiltered'] = data.total
    result['data'] = [['<a href={0}>{1}</a>'.format(
        url_for('studies.show', val=d.pmid),
        d.title),
        d.authors,
        d.journal,
        d.year,
        '<a href=http://www.ncbi.nlm.nih.gov/pubmed/{0}>{0}</a>'.format(
            d.pmid)] for d in data.items]
    return jsonify(**result)


# @login_required
# def get_studies_by_expression(expression):
#     decoded_expr = urllib.unquote(expression).lower().strip('"')
#     expr_ids = tasks.get_studies_by_expression.delay(decoded_expr).wait()
#     ids = []
#     if expr_ids:
#         ids = list(expr_ids)
#     return jsonify(ids=ids)


# Begin client side APIs
@bp.route('/<int:val>/analyses/')
def get_study_analyses(val):
    data = Study.query.get(val)
    data = [['<a href={0}>{1}</a>'.format(
        url_for('analyses.show_analysis', id=f.analysis_id), f.analysis.name),
        round(f.frequency, 3),
    ] for f in data.frequencies if f.analysis.type != 'custom']
    return jsonify(data=data)


@bp.route('/<int:val>/peaks/')
def get_study_peaks(val):
    data = Study.query.get(val)
# data=Peak.query.filter_by(pmid=int(val))#attempted optimization. Join
# causes slower performance however
    data = [[p.table, p.x, p.y, p.z] for p in data.peaks]
# data=Peak.query.filter_by(pmid=int(val)).with_entities(Peak.x,Peak.y,Peak.z).all()
# attempted optimization.
    return jsonify(data=data)


@bp.route('/all/')
def get_all_studies():
    """
    :return: JSON object containing all studies
    """
    key = str(Study.query.count())
    if request.headers.get('If-None-Match') == key:
        return '', 304, {}
    all_studies = Study.query.all()
    response = jsonify(dict(studies=[s.serialize() for s in all_studies]))
    response.headers['ETag'] = key
    response.headers['Cache-Control'] = 'max-age=600'
    return response
