from nsweb.core import apimanager
from nsweb.models import Feature
from nsweb.blueprints import add_blueprint
from flask import Blueprint, render_template
import re


features = Blueprint('features', __name__, 
	url_prefix='/features',
	template_folder='../templates/features')

@features.route('/')
def index():
	return render_template('index.html', features=Feature.query.all())

@features.route('/<id>')
def show(id):
	# return features.root_path
	if re.match('\d+$', id):
		feature = Feature.query.get_or_404(id)
	else:
		feature = Feature.query.filter_by(feature=id).first_or_404()
	return render_template('show.html', feature=feature)

add_blueprint(features)


# Begin API stuff
def find_feature(instance_id, **kwargs):
	""" If the passed ID isn't numeric, assume it's a feature name,
	and retrieve the corresponding numeric ID. 
	DOES NOT WORK BECAUSE CANNOT OVERWRITE instance_id. """
	if not re.match('\d+$', instance_id):
		instance_id = Feature.query.filter_by(feature=instance_id).first().id
	pass

def update_result(result, **kwargs):
	""" Rename frequency to study in JSON. """
	if 'frequencies' in result:
		result['studies'] = result.pop('frequencies')
		for s in result['studies']:
			s['frequency'] = round(s['frequency'], 3)


add_blueprint(apimanager.create_api_blueprint(Feature,
                                              methods=['GET'],
                                              collection_name='features',
                                              results_per_page=20,
                                              max_results_per_page=100,
                                              include_columns=['id',
                                                               'feature',
                                                               'num_studies',
                                                               'num_activations',
                                                               # 'frequencies',
                                                               # 'frequencies.pmid',
                                                               # 'frequencies.frequency'
                                                               'images',
                                                               'images.stat',
                                                               'images.feature_id',
                                                               'images.image_file',
                                                               'images.label',
                                                               'studies',
                                                               'studies.pmid'
                                                               ],
                                              preprocessors={
                                              	'GET_SINGLE': [find_feature]
                                              },
                                              postprocessors={
                                              	'GET_SINGLE': [update_result]
                                              }))
