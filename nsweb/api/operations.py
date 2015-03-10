from nsweb.api import bp
from flask import jsonify, request
from nsweb.api.schemas import AnalysisSchema, StudySchema
from nsweb.models.analyses import Analysis
from nsweb.models.studies import Study
from nsweb.core import cache
import re


@bp.route('/analyses/')
# @cache.memoize(timeout=3600)
def get_analyses():
    """
    Retrieve data for one or more analysis objects
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

    # Optional arguments
    analyses = Analysis.query
    if 'type' in request.args:
        type = request.args['type']
        # Disallow custom analyses for now
        if type in ['term', 'topic']:
            analyses = analyses.filter_by(type=type)

    if 'id' in request.args:
        ids = re.split('[\s,]+', request.args['id'].strip(' ,'))
        analyses = analyses.filter(Analysis.id.in_([int(x) for x in ids]))

    analyses = analyses.paginate(page, limit, False).items
    schema = AnalysisSchema(many=True)
    return jsonify(data=schema.dump(analyses).data)


@bp.route('/studies/')
# @cache.memoize(timeout=3600)
def get_studies():
    """
    Retrieve study information
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

    if 'pmid' in request.args:
        ids = re.split('[\s,]+', request.args['pmid'].strip(' ,'))
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
