from nsweb.core import apimanager
from nsweb.models import Image

apimanager().create_api(Image,
                   methods=['GET'],
                   collection_name='images',
                   results_per_page=20,
                   max_results_per_page=100,)
