from mock import MagicMock, Mock, patch
import re
import inspect

from flask_testing import TestCase as Base
from nsweb.core import create_app, db
from nsweb.models import Study, Peak, Feature, Frequency, Image

#this is here for now. Needs to be replaced with the factory later!
from nsweb.helpers import database_builder
from tests.settings import DATA_DIR, PICKLE_DATABASE, FEATURE_DATABASE, PROD_PICKLE_DATABASE

class TestCase(Base):
    def create_app(self):
        '''creates the app and a sqlite database in memory'''
        return create_app('sqlite://', debug=True, aptana=True)

    def setUp(self):
        '''creates tables'''
        db.create_all()

    def tearDown(self):
        '''drops tables'''
        db.session.remove()
        db.drop_all()
    
    def populate_db(self):
        dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)
        (feature_list,feature_data) = database_builder.read_features_text(data_dir=DATA_DIR,feature_database=FEATURE_DATABASE)
        feature_dict = database_builder.add_features(db,feature_list)
        database_builder.add_studies(db, dataset, feature_list, feature_data, feature_dict)
        database_builder.add_images(db, feature_list, feature_dict)
        
    def get_prod_data_fields(self):
        fields = database_builder.read_pickle_database(DATA_DIR, PROD_PICKLE_DATABASE)[0].keys()
        fields = [x for x in fields if not re.search(r'_id', x) and x !='id']
        return fields
    
    def assert_model_equality(self,models, query_models, additional_fields=[]):
        '''This gets the model parameters from init then iterates over the list comparing the models. This may not be the best way, but it works. Also this was supposed to be a test generator, but this is an extension of unittest.TestCase so those aren't allowed'''
        assert len(models)==len(query_models)
        assert len(models) > 0
        fields = inspect.getargspec(models[0].__init__)
        fields.extend(additional_fields)
        for x in range(len(models)):
            for y in fields:
                if isinstance(x, list):
                    self.assert_model_equality(getattr(models, y), getattr(query_models, y))
                else:
                    assert getattr(models[x], y) == getattr(query_models[x], y)

    def assert_model_contains_fields(self,model, fields):
        attributes = dir(model.__init__)
        for x in fields:
            assert x in attributes