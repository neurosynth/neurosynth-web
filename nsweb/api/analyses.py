from flask import Blueprint, url_for, request, jsonify, redirect
from nsweb.models.analyses import (Analysis, AnalysisSet, TopicAnalysis,
                                   TermAnalysis, CustomAnalysis)
from .schemas import AnalysisSchema
from nsweb.api import images
from nsweb.core import cache
from .utils import make_cache_key
import re
from sqlalchemy import asc, desc


bp = Blueprint('api_analyses', __name__, url_prefix='/api/analyses')


@bp.route('/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_analyses():
    """
    Retrieve meta-analysis data
    ---
    tags:
        - analyses
    responses:
        200:
            description: Analysis information
        default:
            description: No analyses found
    parameters:
        - in: query
          name: limit
          description: Maximum number of analyses to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: type
          description: Analysis type
          type: string
          required: false
        - in: query
          name: name
          description: Analysis name(s)
          type: array
          required: false
          collectionFormat: csv
          items:
            type: string
        - in: query
          name: id
          description: Analysis ID(s)
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

    analyses = Analysis.query

    # Can only retrieve analyses of a single type; defaults to terms.
    type = request.args.get('type', 'term')

    valid_types = {
        'term': TermAnalysis,
        'topic': TopicAnalysis,
        'custom': CustomAnalysis
    }
    if type in list(valid_types.keys()):
        analyses = analyses.with_polymorphic(valid_types[type])
        analyses = analyses.filter_by(type=type)
    if type == 'custom':
        analyses = analyses.filter(CustomAnalysis.private == 0)

    # Optional arguments
    if 'id' in request.args:
        ids = re.split('[\s,]+', request.args['id'].strip(' ,'))
        analyses = analyses.filter(Analysis.id.in_([int(x) for x in ids]))

    if 'name' in request.args:
        names = re.split('[\s,]+', request.args['name'].strip(' ,'))
        analyses = analyses.filter(Analysis.name.in_(names))

    analyses = analyses.paginate(page, limit, False).items
    schema = AnalysisSchema(many=True)
    return jsonify(data=schema.dump(analyses).data)


def find_analysis(name, type=None):
    ''' Retrieve analysis by either id (when int) or name (when string) '''
    if re.match('\d+$', name):
        return Analysis.query.get(name)
    query = Analysis.query.filter_by(name=name)
    if type is not None:
        query = query.filter_by(type=type)
    return query.first()


@bp.route('/<int:val>/')
def get_analysis(val):
    analysis = Analysis.query.get(val)
    return jsonify(data=AnalysisSchema().dump(analysis).data)


@bp.route('/<string:val>/images/')
def get_images(val):
    analysis = find_analysis(val)
    images = [{
        'id': img.id,
        'name': img.label,
        'colorPalette': 'red' if 'association' in img.label else 'blue',
        # "intent": (img.stat + ':').capitalize(),
        'url': '/api/images/%s/download' % img.id,
        'visible': 1 if 'association' in img.label else 0,
        'download': '/api/images/%s/download' % img.id,
        'intent': 'z-score'
    } for img in analysis.images if img.display and 'reverse' not in img.label]
    return jsonify(data=images)


@bp.route('/<string:analysis>/images/<string:image>/')
def get_image_file(analysis, image):
    if not isinstance(analysis, Analysis):
        analysis = find_analysis(analysis)
    unthresholded = ('unthresholded' in list(request.args.keys()))
    if re.match('\d+$', image):
        img = analysis.images[int(image)]
    elif image in ['uniformity', 'association']:
        img = [i for i in analysis.images if image in i.label][0]
    return images.download(img.id, unthresholded)


@bp.route('/<string:val>/studies/')
def get_studies(val):
    analysis = find_analysis(val)
    if 'dt' in request.args:  # DataTables
        data = []
        for f in analysis.frequencies:
            s = f.study
            link = '<a href={0}>{1}</a>'.format(
                url_for('studies.show', val=s.pmid), s.title)
            data.append([link, s.authors, s.journal, round(f.frequency, 3)])
        data = jsonify(data=data)
    else:
        data = jsonify(studies=[s.pmid for s in analysis.studies])
    return data


@bp.route('/term_names/')
def get_term_names():
    # optimize this later--select only names
    names = [f.name for f in TermAnalysis.query.all()]
    return jsonify(data=names)


@bp.route('/<string:type>/<string:name>/images/<string:image>/')
def get_term_image_file(type, name, image):
    type = type.strip('s')  # e.g., 'topics' => 'topic'
    analysis = find_analysis(name, type=type)
    return get_image_file(analysis, image)


@bp.route('/topics/<string:topic_set>/<string:number>/images/<string:image>/')
def get_topic_image_file(topic_set, number, image):
    analysis = TopicAnalysis.query.join(AnalysisSet).filter(
        TopicAnalysis.number == int(number),
        AnalysisSet.name == topic_set).first()
    return get_image_file(analysis, image)


@bp.route('/terms/')
def list_terms():

    results_per_page = int(request.args['length'])
    offset = int(request.args['start'])

    data = TermAnalysis.query

    search = str(request.args['search[value]']).strip()
    if search:  # No empty search on my watch
        search = '%{}%'.format(search)
        data = data.filter(TermAnalysis.name.ilike(search))

    direction = str(request.args['order[0][dir]'])
    ord_col = ['name', 'n_studies', 'n_activations'][
        int(request.args['order[0][column]'])]
    dir_func = asc if direction == 'asc' else desc
    data = data.order_by(dir_func(ord_col))

    data = data.paginate(page=(offset / results_per_page) + 1,
                         per_page=results_per_page, error_out=False)
    result = {}
    result['draw'] = int(request.args['draw'])  # for security
    result['recordsTotal'] = TermAnalysis.query.count()
    result['recordsFiltered'] = data.total
    result['data'] = [
        ['<a href={0}>{1}</a>'.format(
            url_for('analyses.show_term', term=d.name), d.name),
         d.n_studies,
         d.n_activations,
         ] for d in data.items]
    return jsonify(**result)


@bp.route('/topics/')
def list_topic_sets():
    topic_sets = AnalysisSet.query.filter_by(type='topics').all()
    data = [[
        '<a href={0}>{1}</a>'.format(
            url_for('analyses.show_topic_set', topic_set=ts.name),
            ts.name),
        ts.description,
        ts.n_analyses] for ts in topic_sets]
    return jsonify(data=data)


@bp.route('/topics/<string:topic_set>/')
def list_topics(topic_set):
    ts = AnalysisSet.query.filter_by(name=topic_set).first()
    data = [
        ['<a href={0}>{1}</a>'.format(
            url_for('analyses.show_topic', topic_set=ts.name,
                    number=t.number), 'Topic ' + str(t.number).zfill(3)),
         t.terms,
         t.n_studies
         ] for t in ts.analyses]
    return jsonify(data=data)


@bp.route('/analyses/<string:name>/')
def find_api_analysis(name):
    """ If the passed val isn't numeric, assume it's a analysis name,
    and retrieve the corresponding numeric ID.
    """
    val = Analysis.query.filter_by(name=name).first().id
    return redirect(url_for('analyses.api', id=val))


@bp.route('/analyses/<int:val>/')
def analyses_api(val):
    data = Analysis.query.get(val)
# data=Frequency.query.filter_by(analysis_id=int(val))#attempted
# optimization. Join causes slower performance however
    data = [['<a href={0}>{1}</a>'.format(url_for('studies.show', val=f.pmid),
                                          f.study.title),
             f.study.authors,
             f.study.journal,
             f.study.year,
             round(f.frequency, 3),
             ] for f in data.frequencies]
    return jsonify(aaData=data)
