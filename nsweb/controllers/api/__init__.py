from nsweb.core import add_blueprint#, db
from flask import Blueprint #, redirect, jsonify, url_for, request
# from flask_sqlalchemy import sqlalchemy

bp = Blueprint('apis',__name__,url_prefix='/api')

from nsweb.controllers.api.features import *
from nsweb.controllers.api.studies import *
from nsweb.controllers.api.locations import *

add_blueprint(bp)