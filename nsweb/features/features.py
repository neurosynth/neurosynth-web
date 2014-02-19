from nsweb.core import app
from nsweb.core import manager
from nsweb.models import features

manager.create_api(features.Feature,
                   methods=['GET'],
                   collection_name='feature',
                   results_per_page=20,
                   max_results_per_page=100,
                   include_columns=['id',
                                    'feature',
                                    'num_studies',
                                    'num_activations'])
app.run()
