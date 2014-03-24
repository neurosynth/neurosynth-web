from nsweb.core import apimanager, add_blueprint
from nsweb.models import Image

add_blueprint(apimanager.create_api_blueprint(Image,
                                              methods=['GET'],
                                              collection_name='images',
                                              results_per_page=20,
                                              max_results_per_page=100,
                                              include_columns=['id',
                                                               'image_file',
                                                               'label']
                                              ))

