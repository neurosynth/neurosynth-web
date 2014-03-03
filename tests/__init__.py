from nose.tools import ok_, eq_, raises
from mock import MagicMock, Mock, patch

from flask_testing import TestCase as Base

from nsweb.core import create_app, db
from nsweb.helpers import database_builder
from nsweb.models import Study, Peak, Feature, Frequency, Image

import factory

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
        '''creates a clean empty database'''
        database_builder.init_database(db)

    def teardown(self):
        '''does nothing'''
        pass
    
    

if __name__ == "__main__":
    import nose
    nose.run()