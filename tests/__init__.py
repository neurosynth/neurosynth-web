from nose.tools import ok_, eq_, raises
from mock import MagicMock, Mock, patch, self

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

    def setup_module(self):
        '''does nothing'''

    def teardown_module(self):
        '''does nothing'''
        pass

    def setup(self):
        '''creates tables'''
        db.create_all()

    def teardown(self):
        '''drops tables'''
        db.drop_all()
    
    def populate_db(self):
        dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)
        (feature_list,feature_data) = database_builder.read_features_text(data_dir=DATA_DIR,feature_database=FEATURE_DATABASE)
        feature_dict = database_builder.add_features(db,feature_list)
        database_builder.add_studies(db, dataset, feature_list, feature_data, feature_dict)
        database_builder.add_images(db, feature_list, feature_dict)
        
    def get_prod_data_fields(self):
        return database_builder.read_pickle_database(DATA_DIR, PROD_PICKLE_DATABASE)[0].keys()


if __name__ == "__main__":
    import nose
    nose.run()