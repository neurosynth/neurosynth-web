from nsweb.core import app
from nsweb.core import manager
from nsweb.models import studies

manager.create_api(studies.Study,
                   methods=['GET'],
                   collection_name='studies',
                   results_per_page=20,
                   max_results_per_page=100,)
#app.run()
