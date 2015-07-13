from nsweb.api import bp
from flask import jsonify, request
from nsweb.api.schemas import (AnalysisSchema, StudySchema, LocationSchema,
                               ImageSchema, DecodingSchema, GeneSchema)
from nsweb.models.images import Image
from nsweb.models.analyses import (Analysis, TermAnalysis, TopicAnalysis,
                                   CustomAnalysis)
from nsweb.models.locations import Location
from nsweb.models.studies import Study
from nsweb.models.frequencies import Frequency
from nsweb.models.peaks import Peak
from nsweb.models.decodings import Decoding
from nsweb.models.genes import Gene
from nsweb.controllers import decode
from nsweb.controllers.locations import check_xyz
from nsweb.core import cache
from sqlalchemy import func
from sqlalchemy.orm import with_polymorphic
import re


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string


@bp.route('/analyses/')
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
    if type in valid_types.keys():
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


@bp.route('/studies/')
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


@bp.route('/locations/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_location():
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
          description: x-coordinate
          required: true
          type: integer
        - in: query
          name: y
          description: y-coordinate
          required: true
          type: integer
        - in: query
          name: z
          description: z-coordinate
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

    # Check validity of coordinates and redirect if necessary
    check_xyz(x, y, z)

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
@cache.cached(timeout=3600, key_prefix=make_cache_key)
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


@bp.route('/decode/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_decoding():
    """
    Retrieve decoding data for a single image
    ---
    tags:
        - decode
    responses:
        200:
            description: Decoding data
        default:
            description: Decoding not found
    parameters:
        - in: query
          name: uuid
          description: UUID of the decoding
          required: false
          type: string
        - in: query
          name: image
          description: ID of image to decode
          type: integer
          required: false
        - in: query
          name: neurovault
          description: NeuroVault ID of image to decode
          type: integer
          required: false
        - in: query
          name: url
          description: URL of Nifti image to decode
          type: string
          required: false
    """
    dec = Decoding.query.filter_by(display=1)

    if 'uuid' in request.args:
        dec = dec.filter_by(uuid=request.args['uuid']).first()

    elif 'image' in request.args:
        dec = decode.decode_analysis_image(request.args['image'])

    elif 'neurovault' in request.args:
        dec_id = decode.decode_neurovault(request.args['neurovault'],
                                          render=False)
        dec = dec.filter_by(uuid=dec_id).first()

    elif 'url' in request.args:
        dec_id = decode.decode_url(request.args['url'], render=False)
        dec = dec.filter_by(uuid=dec_id).first()

    schema = DecodingSchema()
    return jsonify(data=schema.dump(dec).data)


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
