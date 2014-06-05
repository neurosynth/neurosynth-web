from flask import Blueprint, render_template
from . import route
from ..blueprints import add_blueprint
import random

bp = Blueprint('home', __name__)

@route(bp, '/')
def index():
    """Returns the homepage."""
    img = random.choice(['emotion', 'pain', 'language', 'attention', 'memory', 'motor', 'reward', 'sensation'])
    image = Image.where(:name => "feature_#{img}_reverse").joins(:feature).select(['images.id', 'images.name', 'features.name', 'features.n_studies']).first
    news_items = [] #NewsItem.paginate(:page => params[:page], :per_page => 3).order('created_at DESC')
    return render_template('index.html.slim',image=image,news_items=news_items)

add_blueprint(bp)

