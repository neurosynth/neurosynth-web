from nsweb.core import apimanager
from nsweb.models import Study
from nsweb.blueprints import add_blueprint

def update_result(result, **kwargs):
	""" Rename frequency to feature in JSON. 
	Note: this makes the JSON look nice when requests come in at
	/studies/3000, but breaks the native functionality when requests 
	come in at /studies/3000/frequencies.
	"""
	result['features'] = result.pop('frequencies')
	for f in result['features']:
		f['frequency'] = round(f['frequency'], 3)
	pass


add_blueprint(apimanager.create_api_blueprint(Study,
                                              methods=['GET'],
                                              collection_name='studies',
                                              results_per_page=20,
                                              max_results_per_page=100,
                                              include_columns=['pmid',
                                                               'title',
                                                               'authors',
                                                               'journal',
                                                               'year',
                                                               'peaks',
                                                               'peaks.x',
                                                               'peaks.y',
                                                               'peaks.z',
                                                               'frequencies',
                                                               'frequencies.frequency',
                                                               'frequencies.feature_id'
                                                               ],
                                              postprocessors={
                                              	'GET_SINGLE': [update_result]
                                              }))
