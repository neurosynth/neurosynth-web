from nsweb.core import add_blueprint
from nsweb.models import Location
from flask import Blueprint, render_template

bp = Blueprint('locations',__name__,url_prefix='/locations')

@bp.route('/')
def index():
	return render_template('locations/index.html')

@bp.route('/<id>')
def show(id):
	xyz = [int(i) for i in id.split('_')]
	radius=6
	peaks = Location.closestPeaks(radius,xyz[0],xyz[1],xyz[2])
	return render_template('locations/show.html', peaks=peaks, xyz=xyz)
add_blueprint(bp)

# Begin API stuff
# add_blueprint(apimanager.create_api_blueprint(Location,
#                                               methods=['GET'],
#                                               collection_name='locations',
#                                               results_per_page=20,
#                                               max_results_per_page=100))

