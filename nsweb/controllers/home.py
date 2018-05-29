from flask import Blueprint, render_template, redirect, url_for
from nsweb.core import add_blueprint
from nsweb.models.analyses import TermAnalysis
from nsweb.models.studies import Study
from nsweb.models.locations import Location
from nsweb.models.decodings import Decoding
from nsweb.models.downloads import Download
from nsweb.models.peaks import Peak
import random
import simplejson as json
from nsweb.initializers import settings
from os.path import join
from sqlalchemy import func, distinct
from nsweb.core import db

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    """ Returns the homepage. """
    stats = {
        'n_analyses': db.session.query(func.count(TermAnalysis.id)).first()[0],
        'n_studies': db.session.query(func.count(Study.pmid)).first()[0],
        'n_peaks': db.session.query(func.count(Peak.id)).first()[0],
        # 'n_analyses': TermAnalysis.query.count(),
        # 'n_studies': Study.query.count(),
        # 'n_peaks': Peak.query.count(),
        # 'n_locations': Location.query.count(),
        # 'n_decodings': Decoding.query.count(),
        # 'n_downloads': Download.query.count(),
        # 'n_journals': db.session.query(
        #     func.count(distinct(Study.journal))).first()[0]
    }
    analysis = random.choice(
        ['reward', 'language', 'emotion', 'pain', 'working memory'])
    analysis = TermAnalysis.query.filter_by(name=analysis).first()
    return render_template('home/index.html.slim', analysis=analysis,
                           stats=stats)


@bp.route('/faq/')
def faq():
    data = json.load(open(join(settings.ROOT_DIR, 'data', 'json', 'faq.json')))
    return render_template('home/faq.html.slim', data=data)

@bp.route('/code/')
def code():
    return render_template('home/code.html.slim')


@bp.route('/about/')
def about():
    return render_template('home/about.html.slim')

# Redirect legacy routes


@bp.route('/features/')
def old_feature_index():
    return redirect(url_for('analyses.list_terms'))


@bp.route('/features/<string:val>')
def old_feature_show(val):
    return redirect(url_for('analyses.show_term', term=val))

add_blueprint(bp)
