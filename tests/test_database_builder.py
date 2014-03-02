from mock import MagicMock, Mock, patch
from flask_testing import TestCase

from nsweb.helpers import database_builder


class Test(TestCase):
    def setUp(self):
        database_builder.init_database(self.db)

    def tearDown(self):
        pass

    def setup_module(self):
        from nsweb.core import create_app, db
        create_app('sqlite://', debug=True, aptana=True)
        self.db=db

    def teardown_module(self):
        pass

    def test_initialize_database(self):
        '''Clears and sets up tables in database. The tables in studies, features, and images should exist, but no data'''
        database_builder.init_database(self.db)
        
        for()
        
if __name__ == "__main__":
    import nose
    nose.run()