from flask import Blueprint, render_template
from nsweb.core import add_blueprint
from nsweb.models import Analysis
import random
import simplejson as json
from nsweb.initializers import settings
from os.path import join
from nsweb.models import Analysis, Study, Location, Decoding, Download, Peak
from sqlalchemy import func, distinct
from nsweb.core import db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """ Returns the homepage. """
    stats = {
    	'n_analyses': Analysis.query.count(),
    	'n_studies': Study.query.count(),
    	'n_peaks': Peak.query.count(),
    	'n_locations': Location.query.count(),
    	'n_decodings': Decoding.query.count(),
    	'n_downloads': Download.query.count(),
    	'n_journals': db.session.query(func.count(distinct(Study.journal))).first()[0]
    }

    img = random.choice(['emotion', 'pain', 'language', 'attention', 'memory', 'motor', 'reward', 'sensation'])
    # image = Image.where(:name => "analysis_#{img}_reverse").joins(:analysis).select(['images.id', 'images.name', 'analyses.name', 'analyses.n_studies']).first
    # news_items = [] #NewsItem.paginate(:page => params[:page], :per_page => 3).order('created_at DESC')
    analysis = random.choice(['reward', 'language', 'emotion', 'pain', 'working memory'])
    analysis = Analysis.query.filter_by(name=analysis).first()
    return render_template('home/index.html.slim', analysis=analysis, stats=stats)

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

add_blueprint(bp)

