from nsweb.core import apimanager, add_blueprint
from nsweb.models import Location
from flask import Blueprint, render_template
import re


locations = Blueprint('locations', __name__, 
	url_prefix='/locations')

@locations.route('/')
def index():
	return render_template('locations/index.html')

@locations.route('/<id>')
def show(id):
	if re.search('_', id):
		x, y, z = [float(i) for i in id.split('_')]
		location = Location.query.filter_by(x=x, y=y, z=z).first()
	else:
		location = Location.query.get_or_404(id)
	return render_template('locations/show.html', location=location)

add_blueprint(locations)


# Begin API stuff
add_blueprint(apimanager.create_api_blueprint(Location,
                                              methods=['GET'],
                                              collection_name='locations',
                                              results_per_page=20,
                                              max_results_per_page=100))

