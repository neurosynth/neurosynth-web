from flask import Blueprint, render_template
from nsweb.core import add_blueprint
import random

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """ Returns the homepage. """
    img = random.choice(['emotion', 'pain', 'language', 'attention', 'memory', 'motor', 'reward', 'sensation'])
    # image = Image.where(:name => "feature_#{img}_reverse").joins(:feature).select(['images.id', 'images.name', 'features.name', 'features.n_studies']).first
    # news_items = [] #NewsItem.paginate(:page => params[:page], :per_page => 3).order('created_at DESC')
    return render_template('home/index.html.slim')

add_blueprint(bp)

