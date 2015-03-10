from nsweb.core import add_blueprint
from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from nsweb.controllers.api.analyses import *
from nsweb.controllers.api.studies import *
from nsweb.controllers.api.locations import *

add_blueprint(bp)
