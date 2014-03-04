from nsweb.core import apimanager
from nsweb.models import Feature
from nsweb.blueprints import add_blueprint

add_blueprint(apimanager.create_api_blueprint(Feature,
                                              methods=['GET'],
                                              collection_name='images',
                                              results_per_page=20,
                                              max_results_per_page=100,))
