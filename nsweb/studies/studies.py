import flask
import flask_sqlalchemy
import flask_restless
import pickle
import nsweb.models.TOREMOVEmodels
from nsweb.models import TOREMOVEmodels
from mako.ext import preprocessors

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = flask_sqlalchemy.SQLAlchemy(app)
manager = flask_restless.APIManager(app,flask_sqlalchemy_db=db)

#def pre_get_single(**kw): pass
#def pre_get_many(**kw): pass
#def get_single_preprocessor(instance_id=None, **kw):
#    """Accepts a single argument, `instance_id`, the primary key of the
#    instance of the model to get.
#
#    """
#    pass
manager.create_api(TOREMOVEmodels.Study,
                   methods=['GET'],
                   results_per_page=20,
                   max_results_per_page=100,
#                   preprocessors={'GET_SINGLE':[get_single_preprocessor]}
)
app.run()