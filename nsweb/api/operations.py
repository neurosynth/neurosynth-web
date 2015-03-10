from nsweb.api import bp
from flask import jsonify, request
from nsweb.api.schemas import (AnalysisSchema, StudySchema, LocationSchema,
                               ImageSchema)
from nsweb.models.images import Image
from nsweb.models.analyses import Analysis
from nsweb.models.locations import Location
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak
from nsweb.core import cache
from sqlalchemy import func
import re


@bp.route('/analyses/')
# @cache.memoize(timeout=3600)
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

    if 'name' in request.args:
        names = re.split('[\s,]+', request.args['name'].strip(' ,'))
        analyses = analyses.filter(Analysis.name.in_(names))

    analyses = analyses.paginate(page, limit, False).items
    schema = AnalysisSchema(many=True)
    return jsonify(data=schema.dump(analyses).data)


@bp.route('/studies/')
# @cache.memoize(timeout=3600)
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


@bp.route('/locations/')
# @cache.memoize(timeout=3600)
def get_locations():
    """
    Retrieve location data
    ---
    tags:
        - locations
    responses:
        200:
            description: Location data
        default:
            description: No locations found
    parameters:
        - in: query
          name: x
          description: x-coordinate(s)
          required: true
          type: integer
        - in: query
          name: y
          description: y-coordinate(s)
          required: true
          type: integer
        - in: query
          name: z
          description: z-coordinate(s)
          required: true
          type: integer
        - in: query
          name: r
          description: Radius of sphere within which to search for study activations, in mm (default = 6, max = 20).
          required: false
          type: integer
    """
    x = int(request.args['x'])
    y = int(request.args['y'])
    z = int(request.args['z'])
    #  Radius: 6 mm by default, max 2 cm
    r = min(int(request.args.get('r', 6)), 20)

    loc = Location.query.filter_by(x=x, y=y, z=z).first()
    if loc is None:
        from nsweb.controllers.locations import make_location
        loc = make_location(x, y, z)

    peaks = Peak.closestPeaks(r, x, y, z)
    peaks = peaks.group_by(Peak.pmid)
    peaks = peaks.add_columns(func.count(Peak.id))

    loc.studies = [p[0].study for p in peaks]

    schema = LocationSchema()
    return jsonify(data=schema.dump(loc).data)


@bp.route('/images/')
# @cache.memoize(timeout=3600)
def get_images():
    """
    Retrieve image data
    ---
    tags:
        - images
    responses:
        200:
            description: Image data
        default:
            description: No images found
    parameters:
        - in: query
          name: limit
          description: Maximum number of images to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: search
          description: Search image fields (label, description)
          type: string
          required: false
        - in: query
          name: id
          description: PubMed ID(s) of one or more studies
          required: false
          collectionFormat: csv
          type: array
          items:
            type: integer
        - in: query
          name: type
          description: Associated object type
          type: string
          required: false
    """
    DEFAULT_LIMIT = 25
    MAX_LIMIT = 100
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    limit = min(limit, MAX_LIMIT)
    page = int(request.args.get('page', 1))

    images = Image.query.filter_by(display=1, download=1)

    if 'type' in request.args:
        images = images.filter_by(type=request.args['type'])

    if 'id' in request.args:
        ids = re.split('[\s,]+', request.args['id'].strip(' ,'))
        images = images.filter(Image.id.in_([int(x) for x in ids]))

    if 'search' in request.args and len(request.args['search']) > 1:
        search = '%{}%'.format(request.args['search'])
        images = images.filter(Image.label.like(search) |
                               Image.description.like(search))

    images = images.paginate(page, limit, False).items
    schema = ImageSchema(many=True)
    return jsonify(data=schema.dump(images).data)
