import urllib

from nsweb.controllers.api import bp
from flask import request, jsonify, url_for
from nsweb.models.studies import Study
from flask_user import login_required
from nsweb import tasks
from nsweb.core import cache
import re

# Begin server side APIs


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string


@bp.route('/studies/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_study_list():

    if 'expression' in request.args:
        return get_studies_by_expression(request.args['expression'])

    data = Study.query
    results_per_page = int(request.args['length'])
    offset = int(request.args['start'])
    order_by = '{0} {1}'.format(
        ['title', 'authors', 'journal', 'year', 'pmid']
        [int(request.args['order[0][column]'])],
        str(request.args['order[0][dir]']))
    search = str(request.args['search[value]']).strip()
    if search:  # No empty search on my watch
        search = '%{}%'.format(search)
        data = data.filter(Study.title.like(search) |
                           Study.authors.like(search) |
                           Study.journal.like(search) |
                           Study.year.like(search) |
                           Study.pmid.like(search))
    data = data.order_by(order_by)
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
        '<a href=http://www.ncbi.nlm.nih.gov/pubmed/{0}>{0}</a>'.format(d.pmid)] for d in data.items]
    result = jsonify(**result)
    return result


@login_required
def get_studies_by_expression(expression):
    decoded_expr = urllib.unquote(expression).lower().strip('"')
    expr_ids = tasks.get_studies_by_expression.delay(decoded_expr).wait()
    ids = []
    if expr_ids:
        ids = list(expr_ids)
    return jsonify(ids=ids)


# Begin client side APIs
@bp.route('/studies/analyses/<int:val>/')
def get_study_analyses(val):
    data = Study.query.get(val)
    data = [['<a href={0}>{1}</a>'.format(
        url_for('analyses.show_analysis', id=f.analysis_id), f.analysis.name),
        round(f.frequency, 3),
    ] for f in data.frequencies if f.analysis.type != 'custom']
    data = jsonify(data=data)
    return data


@bp.route('/studies/peaks/<int:val>/')
def get_study_peaks(val):
    data = Study.query.get(val)
# data=Peak.query.filter_by(pmid=int(val))#attempted optimization. Join
# causes slower performance however
    data = [[p.table, p.x, p.y, p.z] for p in data.peaks]
# data=Peak.query.filter_by(pmid=int(val)).with_entities(Peak.x,Peak.y,Peak.z).all()
# attempted optimization.
    data = jsonify(data=data)
    return data

@bp.route('/studies/all/')
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

