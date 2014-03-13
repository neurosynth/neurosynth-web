from nsweb.core import apimanager
from nsweb.models import Location
from nsweb.blueprints import add_blueprint

add_blueprint(apimanager.create_api_blueprint(Location,
                                              methods=['GET'],
                                              collection_name='locations',
                                              results_per_page=20,
                                              max_results_per_page=100))

