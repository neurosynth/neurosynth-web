from nsweb.core import apimanager
from nsweb.models import studies

apimanager().create_api(studies.Study,
                   methods=['GET'],
                   collection_name='studies',
                   results_per_page=20,
                   max_results_per_page=100,)
