from nsweb.core import apimanager
from nsweb.models import Study
from nsweb.blueprints import add_blueprint
from flask import Blueprint, render_template

studies = Blueprint('studies', __name__, 
	url_prefix='/studies')

@studies.route('/')
def index():
	return render_template('studies/index.html', studies=Study.query.all())

@studies.route('/<id>')
def show(id):
	return render_template('studies/show.html', study=Study.query.get_or_404(id))

add_blueprint(studies)


# Begin API stuff
def update_result(result, **kwargs):
	""" Rename frequency to feature in JSON. 
	Note: this makes the JSON look nice when requests come in at
	/studies/3000, but breaks the native functionality when requests 
	come in at /studies/3000/frequencies.
	"""
	if 'frequencies' in result:
		result['features'] = result.pop('frequencies')
		for f in result['features']:
			f['frequency'] = round(f['frequency'], 3)
		pass

includes=['pmid',
		'title',
		'authors',
		'journal',
		'year',
		'peaks',
		'peaks.x',
		'peaks.y',
		'peaks.z',
		# 'frequencies',
		# 'frequencies.frequency',
		# 'frequencies.feature_id',
		'features',
		'features.feature'
		]
add_blueprint(apimanager.create_api_blueprint(Study,
                                              methods=['GET'],
                                              collection_name='studies',
                                              results_per_page=20,
                                              max_results_per_page=100,
                                              include_columns=includes,
                                              postprocessors={
                                              	'GET_SINGLE': [update_result]
                                              }))
