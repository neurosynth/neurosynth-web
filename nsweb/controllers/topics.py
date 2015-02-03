from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort
from nsweb.models import Topic
from nsweb.core import add_blueprint
from flask.helpers import url_for
import simplejson as json
import re

bp = Blueprint('topics', __name__, url_prefix='/topics')

    
@bp.route('/')
def index():
    return render_template('topics/index.html.slim')

@bp.route('/<string:analysis_set>/<string:analysis>')
def show(val):
    topic = Topic.query.join(AnalysisSet).filter(Topic.name == analysis, AnalysisSet.name == analysis_set).first()
    n_studies = topic.frequencies.count()
    return render_template('analyses/show.html.slim', analysis_set=topic.analysis_set, topic=topic.id, n_studies=n_studies)


add_blueprint(bp)

