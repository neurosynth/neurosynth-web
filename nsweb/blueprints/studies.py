from nsweb.core import apimanager
from nsweb.models import Study
from nsweb.blueprints import add_blueprint

add_blueprint(apimanager.create_api_blueprint(Study,
                                              methods=['GET'],
                                              collection_name='studies',
                                              results_per_page=20,
                                              max_results_per_page=100,
                                              include_columns=['pmid',
                                                               'title',
                                                               'authors',
                                                               'journal',
                                                               'year']))
