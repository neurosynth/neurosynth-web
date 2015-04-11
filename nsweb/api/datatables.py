""" DataTables API routes. These are just wrappers around the routes in
the operations module. """

from nsweb.api import bp
from flask import jsonify, request
from nsweb.api.schemas import (AnalysisSchema, StudySchema, LocationSchema,
                               ImageSchema, DecodingSchema)
from nsweb.models.images import Image
from nsweb.models.analyses import Analysis
from nsweb.models.locations import Location
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak
from nsweb.models.decodings import Decoding
from nsweb.controllers import decode
from nsweb.core import cache
from sqlalchemy import func
import re

@bp.route('/dt/genes/')

