import flask
import flask_sqlalchemy
import flask_restless
import pickle
from mako.ext import preprocessors

from nsweb.core import app
from nsweb.core import manager
from nsweb.models import studies
#from nsweb.models import features

manager.create_api(studies.Study,
                   methods=['GET'],
                   collection_name='study',
                   results_per_page=20,
                   max_results_per_page=100,
#                   url_prefix='/study')
#                    include_columns = ['pmid',
#                                'title',
#                                'journal',
#                                'authors',
#                                'year']
app.run()