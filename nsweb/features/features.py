from nsweb.core import apimanager
from nsweb.models import Feature

apimanager().create_api(Feature,
                   methods=['GET'],
                   collection_name='features',
                   results_per_page=20,
                   max_results_per_page=100,
                   include_columns=['id',
                                    'feature',
                                    'num_studies',
                                    'num_activations'])
