import flask
import flask_sqlalchemy
import flask_restless
import pickle
from mako.ext import preprocessors

from nsweb.core import manager
from nsweb.models import studies
from nsweb.models import features

#def pre_get_single(**kw): pass
#def pre_get_many(**kw): pass
#def get_single_preprocessor(instance_id=None, **kw):
#    """Accepts a single argument, `instance_id`, the primary key of the
#    instance of the model to get.
#
#    """
#    Pass

manager.create_api(studies.Study,
                   methods=['GET'],
                   results_per_page=20,
                   max_results_per_page=100,
#                   preprocessors={'GET_SINGLE':[get_single_preprocessor]}
                   includes = ['pmid',
                               'title',
                               'journal',
                               'authors',
                               'year'])
app.run()